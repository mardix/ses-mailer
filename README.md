# SES Mailer

SES Mailer is wrapper around `boto.ses` to send email via AWS SES

You can use it as standalone or with Flask

Requirements:

- boto
- Your AWS credentials

---

## Install

    pip install ses-mailer

# Usage

### Initiate

    from ses_mailer import Mail

    mail = Mail(aws_access_key_id="####",
                 aws_secret_access_key="####",
                 sender="me@myemail.com",
                 reply_to="me@email.com")

### Initiate with Flask

    from flask import Flask
    from ses_mailer import Mail

    app = Flask(__name__)

    mail = Mail()
    mail.init_app(app)


### Send Email

    mail.send(to="you@email.com",
              subject="My Email subject",
              body="My message body")


### Config For Flask

SES-Mailer is configured through the standard Flask config API.
These are the available options:

**SES_MAILER_AWS_ACCESS_KEY_ID** : Your AWS access key id

**SES_MAILER_AWS_SECRET_ACCESS_KEY**: Your AWS secred key

**SES_MAILER_SENDER**: The sender email address as string.

**SES_MAILER_REPLY_TO**: The reply to address


    SES_MAILER_AWS_ACCESS_KEY_ID = ""
    SES_MAILER_AWS_SECRET_ACCESS_KEY = ""
    SES_MAILER_SENDER = ""
    SES_MAILER_REPLY_TO = ""

---

(c) 2014 Mardix

