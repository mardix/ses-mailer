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



## Template Mail

Template allows you to simply use a template file as your email


    from ses_mailer import TemplateMail

    tmail = TemplateMail(aws_access_key_id="####",
                 aws_secret_access_key="####",
                 sender="me@myemail.com",
                 reply_to="me@email.com",
                 template_dir="./email-templates")

    tmail.send("welcome.txt", to="you@email.com", name="Ricky Roze", user_id=12739)


### Requirements

Each part of the email (subject, body) must be within blocks, and each template
must have a **subject** and a **body** block


welcome.txt


    {% block subject %}Welcome {{name}} to our site {% endblock %}

    {% block body %}Dear {{name}} this is the content of the message {% endblock %}



### Config For Flask

SES-Mailer is configured through the standard Flask config API.
These are the available options:

**SES_MAILER_AWS_ACCESS_KEY_ID** : Your AWS access key id

**SES_MAILER_AWS_SECRET_ACCESS_KEY**: Your AWS secred key

**SES_MAILER_SENDER**: The sender email address as string.

**SES_MAILER_REPLY_TO**: The reply to address

**SES_MAILER_TEMPLATE_DIR**: The directory of template when using TemplateMail

**SES_MAILER_TEMPLATE_MAP**: A map file template when using TemplateMail

**SES_MAILER_TEMPLATE_FILE_EXTENSION**: File extension of template.

**SES_MAILER_TEMPLATE_DEFAULT_CONTEXT**: A dict of default data to be passed by default
when building the template

    SES_MAILER_AWS_ACCESS_KEY_ID = ""
    SES_MAILER_AWS_SECRET_ACCESS_KEY = ""
    SES_MAILER_SENDER = ""
    SES_MAILER_REPLY_TO = ""
    SES_MAILER_TEMPLATE_DIR = None
    SES_MAILER_TEMPLATE_MAP = None
    SES_MAILER_TEMPLATE_FILE_EXTENSION = None
    SES_MAILER_TEMPLATE_DEFAULT_CONTEXT = {}


---

(c) 2014 Mardix

