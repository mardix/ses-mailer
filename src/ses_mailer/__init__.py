"""
A simple module to send email via AWS SES

It also allow you to use templates to send email
"""
import os
import re
import boto3
import botocore
from jinja2 import Environment, FileSystemLoader, DictLoader

class Template(object):
    env = None
    cached_templates = {}

    def __init__(self, template):
        """
        :param template: (string | dict) - The directory or dict of templates
            - as string: A directory
            - as dict: {'index.html': 'source here'}
        """
        loader = None
        if template:
            if isinstance(template, dict):
                loader = DictLoader(template)
            elif os.path.isdir(template):
                loader = FileSystemLoader(template)

            if loader:
                self.env = Environment(loader=loader)

    def _get_template(self, template_name):
        """
        Retrieve the cached version of the template
        """
        if template_name not in self.cached_templates:
            self.cached_templates[template_name] = \
                self.env.get_template(template_name)
        return self.cached_templates[template_name]

    def render_blocks(self, template_name, **context):
        """
        To render all the blocks
        :param template_name: The template file name
        :param context: **kwargs context to render
        :retuns dict: of all the blocks with block_name as key
        """
        blocks = {}
        template = self._get_template(template_name)
        for block in template.blocks:
            blocks[block] = self._render_context(template,
                                                 template.blocks[block],
                                                 **context)
        return blocks

    def render(self, template_name, block, **context):
        """
        TO render a block in the template
        :param template_name: the template file name
        :param block: the name of the block within {% block $block_name %}
        :param context: **kwargs context to render
        :returns string: of rendered content
        """
        template = self._get_template(template_name)
        return self._render_context(template,
                                    template.blocks[block],
                                    **context)

    def _render_context(self, template, block, **context):
        """
        Render a block to a string with its context
        """
        return u''.join(block(template.new_context(context)))


class Mail(object):
    """
    To send basic email
    """
    ses = None
    sender = None
    reply_to = None
    template = None
    template_context = {}

    def __init__(self,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 region='us-west-2',
                 sender=None,
                 reply_to=None,
                 template=None,
                 template_context={},
                 app=None):
        """
        Setup the mail

        """
        if app:
            self.init_app(app)
        else:
            if (aws_access_key_id and aws_secret_access_key):
                self.client = boto3.client('ses',
                region_name = region,
                aws_access_key_id =  aws_access_key_id,
                aws_secret_access_key = aws_secret_access_key
            )
            else:  # credentials from an aws config file
                self.client = boto3.client('ses', region_name='us-west-2')

            self.sender = sender
            self.reply_to = reply_to or self.sender

            if template:
                self.template = Template(template=template)
            if template_context:
                self.template_context = template_context

    def init_app(self, app):
        """
        For Flask using the app config
        """
        self.__init__(
            aws_access_key_id=app.config.get("SES_AWS_ACCESS_KEY"),
            aws_secret_access_key=app.config.get("SES_AWS_SECRET_KEY"),
            region=app.config.get("SES_REGION", "us-east-1"),
            sender=app.config.get("SES_SENDER", None),
            reply_to=app.config.get("SES_REPLY_TO", None),
            template=app.config.get("SES_TEMPLATE", None),
            template_context=app.config.get("SES_TEMPLATE_CONTEXT", {}),
        )

    def send(self, to, subject, body, reply_to=None, sender=None, **kwargs):
        """
        Send email via AWS SES.
        :returns string: message id

        ***

        Composes an email message based on input data, and then immediately
        queues the message for sending.

        :type to: list of strings or string
        :param to: The To: field(s) of the message.

        :type subject: string
        :param subject: The subject of the message: A short summary of the
                        content, which will appear in the recipient's inbox.

        :type body: string
        :param body: The message body.

        :sender: email address of the sender. String or typle(name, email)
        :reply_to: email to reply to

        **kwargs:

        :type cc_addresses: list of strings or string
        :param cc_addresses: The CC: field(s) of the message.

        :type bcc_addresses: list of strings or string
        :param bcc_addresses: The BCC: field(s) of the message.

        :type format: string
        :param format: The format of the message's body, must be either "text"
                       or "html".

        :type return_path: string
        :param return_path: The email address to which bounce notifications are
                            to be forwarded. If the message cannot be delivered
                            to the recipient, then an error message will be
                            returned from the recipient's ISP; this message
                            will then be forwarded to the email address
                            specified by the ReturnPath parameter.

        :type text_body: string
        :param text_body: The text body to send with this email.

        :type html_body: string
        :param html_body: The html body to send with this email.

        """
        if not self.sender and not sender:
            raise AttributeError("Sender email 'sender' is not provided")

        text_body = kwargs.get('text_body', body) 
        html_body = kwargs.get('html_body', body) 

        source = self._get_sender(sender or self.sender)[0]
        destination = {'ToAddresses': self._listify(to),
                       'CcAddresses': self._listify(kwargs.get('cc_addresses',[])),
                       'BccAddresses': self._listify(kwargs.get('bcc_addresses',[]))
        }
        message = {'Subject': {'Data': subject},
                   'Body': {
                       'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                       'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                   }
        }            
        reply_addresses = [self._get_sender(reply_to or self.reply_to)[2]]
  
        try:
            response = self.client.send_email(Source=source,
                Destination=destination, Message=message,
                ReplyToAddresses=reply_addresses )
                #ReturnPath=kwargs.get('return_path',''))

            return response.get('MessageId')
        except ValueError:  #botocore.exceptions.ClientError:
            return None

    def send_template(self, template, to, reply_to=None, **context):
        """
        Send email from template
        """
        mail_data = self.parse_template(template, **context)
        subject = mail_data["subject"]
        body = mail_data["body"]
        del(mail_data["subject"])
        del(mail_data["body"])

        return self.send(to=to,
                         subject=subject,
                         body=body,
                         reply_to=reply_to,
                         **mail_data)

    def parse_template(self, template, **context):
        """
        To parse a template and return all the blocks
        """
        required_blocks = ["subject", "body"]
        optional_blocks = ["text_body", "html_body", "return_path", "format"]

        if self.template_context:
            context = dict(list(self.template_context.items()) +
                           list(context.items()))
        blocks = self.template.render_blocks(template, **context)

        for rb in required_blocks:
            if rb not in blocks:
                raise AttributeError(
                    "Template error: block '%s' is missing from '%s'" %
                    (rb, template))

        mail_params = {
            "subject": blocks["subject"].strip(),
            "body": blocks["body"]
        }
        for ob in optional_blocks:
            if ob in blocks:
                if ob == "format" and \
                        blocks[ob].lower() not in ["html", "text"]:
                    continue
                mail_params[ob] = blocks[ob]
        return mail_params

    def _get_sender(self, sender):
        """
        Return a tuple of 3 elements
            0: the email signature "Me <email@me.com>"
            1: the name "Me"
            2: the email address "email@me.com"

        if sender is an email string, all 3 elements will be the email address
        """
        if isinstance(sender, tuple):
            return "%s <%s>" % sender, sender[0], sender[1]
        else:
            return sender, sender, sender
    
    def _listify(self, maybe_str):
        if type(maybe_str) == str or type(maybe_str) == unicode:
            return [maybe_str]
        return maybe_str    
