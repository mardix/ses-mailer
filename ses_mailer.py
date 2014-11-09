"""
SES-Mailer

A wrapper around boto ses to send email via AWS SES

"""
import re
import boto


__NAME__ = "SES-Mailer"
__version__ = "0.2"
__license__ = "MIT"
__author__ = "Mardix"
__copyright__ = "(c) 2014 Mardix"


def is_email_valid(email):
    """
    Check if email is valid
    """
    pattern = '[\w\.-]+@[\w\.-]+[.]\w+'
    return re.match(pattern, email)


class Mail():

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
        Send email via AWS SES

        *** Must have the config key: MAILER with 'from'

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

        return self.ses.send_email(**kwargs)


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

    def add_attachment(self):
        pass
