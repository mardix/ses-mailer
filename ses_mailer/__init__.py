"""
SES-Mailer

A wrapper around boto ses to send email via AWS

It also allow you to use files as template to send email

"""
import os
import re
try:
    import boto
except ImportError as ex:
    print("Boto is missing. pip --install boto")
try:
    from jinja2 import Environment, FileSystemLoader, DictLoader
except ImportError as ex:
    print("Jinja2 is missing. pip --install jinja2")


__NAME__ = "SES-Mailer"
__version__ = "0.5.2"
__license__ = "MIT"
__author__ = "Mardix"
__copyright__ = "(c) 2014 Mardix"


def is_valid_email(email):
    """
    Check if email is valid
    """
    pattern = '[\w\.-]+@[\w\.-]+[.]\w+'
    return re.match(pattern, email)


class Template(object):

    env = None
    file_extension = None
    chached_templates = {}

    def __init__(self,
                 template_dir=None,
                 template_map=None,
                 file_extension=None):
        """
        :param template_dir: string - The directory containing all the template files
        :param template_map: dict - a dict of template to load
                                    ->
                                    {'index.html': 'source here'}
        :param file_extension: string of file extension containing the leading dot
                                    -> .html
        """
        loader = None
        if template_dir:
            loader = FileSystemLoader(template_dir)
        elif template_map:
            if not isinstance(template_map, dict):
                raise TypeError("Invalid type. 'template_map' must be of type dict")
            loader = DictLoader(template_map)
        if loader:
            self.env = Environment(loader=loader)
        self.file_extension = file_extension

    def _get_template(self, template_name):
        """
        Retrieve the cached version of the template
        """
        template_name = self._add_file_extension(template_name)
        if template_name not in self.chached_templates:
            self.chached_templates[template_name] = self.env.get_template(template_name)
        return self.chached_templates[template_name]

    def _add_file_extension(self, file):
        """
        Add  extension to a file if necessary
        """
        if self.file_extension:
            if os.path.splitext(file)[1]:
                return file
            else:
                return file + self.file_extension
        return file

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


    def __init__(self,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 sender=None,
                 reply_to=None):

        if aws_access_key_id and aws_secret_access_key:
            self.ses = boto.connect_ses(aws_access_key_id=aws_access_key_id,
                                        aws_secret_access_key=aws_secret_access_key)
        if sender:
            self.sender = sender
        if reply_to:
            self.reply_to = reply_to


    def init_app(self, app):
        """
        For Flask using the app config
        """
        self.__init__(aws_access_key_id=app.config.get("SES_MAILER_AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=app.config.get("SES_MAILER_AWS_SECRET_ACCESS_KEY"),
                      sender=app.config.get("SES_MAILER_SENDER", None),
                      reply_to=app.config.get("SES_MAILER_REPLY_TO", None))


    def send(self, to, subject, body, **kwargs):
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

        **kwargs:

        :type source: string
        :param source: The sender's email address.

        :type cc_addresses: list of strings or string
        :param cc_addresses: The CC: field(s) of the message.

        :type bcc_addresses: list of strings or string
        :param bcc_addresses: The BCC: field(s) of the message.

        :type format: string
        :param format: The format of the message's body, must be either "text"
                       or "html".

        :type reply_addresses: list of strings or string
        :param reply_addresses: The reply-to email address(es) for the
                                message. If the recipient replies to the
                                message, each reply-to address will
                                receive the reply.

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
        kwargs["to_addresses"] = to
        kwargs["subject"] = subject
        kwargs["body"] = body

        if "source" not in kwargs:
            if not self.sender:
                raise TypeError("Sender email is not provided")
            kwargs["source"] = self._get_sender(self.sender)[0]

        if "reply_addresses" not in kwargs:
            if self.reply_to:
                reply_to = self.reply_to
            elif self.sender:
                reply_to = self._get_sender(self.sender)[2]
            kwargs["reply_addresses"] = [reply_to]

        response = self.ses.send_email(**kwargs)
        return response["SendEmailResponse"]["SendEmailResult"]["MessageId"]


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


class TemplateMail(object):
    """
    To send email using templates

    tmail = TemplateMail()

    > to send email

    tmail.send("welcome", to="you@yahoo.com", name="You", email="you@yahoo.com")
    """
    mail = None
    template = None
    default_context = {}

    def __init__(self,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 sender=None,
                 template_dir=None,
                 template_map=None,
                 file_extension=None,
                 reply_to=None,
                 default_context={}):

        if aws_access_key_id and aws_secret_access_key:
            self.mail = Mail(aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             sender=sender,
                             reply_to=reply_to)

        if template_dir or template_map:
            self.template = Template(template_dir=template_dir,
                                     template_map=template_map,
                                     file_extension=file_extension)
        if default_context:
            self.default_context = default_context

    def init_app(self, app):
        self.mail = Mail()
        self.mail.init_app(app)
        self.template = Template(template_dir=app.config.get("SES_MAILER_TEMPLATE_DIR", None),
                                 template_map=app.config.get("SES_MAILER_TEMPLATE_MAP", None),
                                 file_extension=app.config.get("SES_MAILER_TEMPLATE_FILE_EXTENSION", None)
                                 )
        self.default_context = app.config.get("SES_MAILER_TEMPLATE_DEFAULT_CONTEXT", {})


    def send(self, template_name, to, **context):
        """
        To send email using template
        """
        required_blocks = ["subject", "body"]
        optional_blocks = ["text_body", "html_body", "return_path", "format"]

        if self.default_context:
            context = dict(self.default_context.items() + context.items())
        blocks = self.template.render_blocks(template_name, **context)

        for rb in required_blocks:
            if rb not in blocks:
                raise AttributeError("Template error: block '%s' is missing from '%s'" % (rb, template_name))

        mail_params = {}
        for ob in optional_blocks:
            if ob in blocks:
                if ob == "format" and mail_params[ob] not in ["html", "text"]:
                    continue
                mail_params[ob] = blocks[ob]

        subject = blocks["subject"].strip()
        body = blocks["body"]

        return self.mail.send(to=to, subject=subject, body=body, **mail_params)


