# SES Mailer

A simple module to send email via AWS SES 

You can use it as standalone or with Flask

Requirements:

- AWS Credentials
- boto
- Jinja

---

## Install

    pip install ses-mailer

## Usage

### Setup

    from ses_mailer import Mail

    mail = Mail(aws_access_key_id="####",
                 aws_secret_access_key="####",
                 sender="me@myemail.com",
                 reply_to="me@email.com",
                 template="./email-templates")
                 
#### Send Basic Email

    mail.send(to="you@email.com",
              subject="My Email subject",
              body="My message body")
              
#### Send Template Email

    mail.send_template(template="welcome.txt", 
                       to="you@email.com", 
                       name="Ricky Roze", 
                       user_id=12739)
     

##API

**Mail.\__init__**

	- aws_access_key_id
	- aws_secret_access_key
	- sender
	- reply_to
	- template
	
**Mail.send**

	- to
	- subject
	- body
	- reply_to
		
**Mail.send_template**

	- template
	- to
	- reply_to
	- **context	
     
     
### Initiate with Flask

    from flask import Flask
    from ses_mailer import Mail

    app = Flask(__name__)

    mail = Mail()
    mail.init_app(app)


## Templates

You can use pre-made templates to send email

The template must be a Jinja template, containing at least the following blocks:

    - subject
    - body
    

welcome.txt

    {% block subject %}
        Welcome {{name}} to our site 
    {% endblock %}

    {% block body %}
        Dear {{name}} this is the content of the message 
        
        Thank you very much for your visiting us
    {% endblock %}


### File Templates:

Place you template files inside of a directory, let's say: `email-templates`

Inside of `email-templates` we have the following files:

    /email-templates
        |
        |_ welcome.txt
        |
        |_ lost-password.txt
        
        
    mail = Mail(aws_access_key_id="####",
                 aws_secret_access_key="####",
                 sender="me@myemail.com",
                 reply_to="me@email.com",
                 template="./email-templates")

### Dictionary based templates

If you don't want to create files, you can dictionary based templates

    templates = {
        "welcome.txt": """
            {% block subject %}I'm subject{% endblock %}
            {% block body %}How are you {{name}}?{% endblock %}
        """,
        "lost-password.txt": """
            {% block subject %}Lost Password{% endblock %}
            {% block body %}Hello {{ name }}. 
            Here's your new password: {{ new_password }} 
            {% endblock %}
        """,    
    }
    
    mail = Mail(aws_access_key_id="####",
                 aws_secret_access_key="####",
                 sender="me@myemail.com",
                 reply_to="me@email.com",
                 template=templates)

To send the email for either files or dictionary based templates:
    
    new_password = "mynewpassword"
    mail.send_template("lost-password.txt", to="x@y.com", name="Lolo", new_password=new_password)

### Config For Flask

SES-Mailer is configured through the standard Flask config API.
These are the available options:

**AWS_ACCESS_KEY_ID** : Your AWS access key id

**AWS_SECRET_ACCESS_KEY**: Your AWS secred key

**SES_SENDER**: The sender email address as string.

**SES_REPLY_TO**: The reply to address

**SES_TEMPLATE**: (mixed) directory or dict of template to use as template

**SES_TEMPLATE_CONTEXT**: A dict of default data to be passed by default

    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""
    SES_SENDER = ""
    SES_REPLY_TO = ""
    SES_TEMPLATE = None
    SES_TEMPLATE_CONTEXT = {}


---

(c) 2015 Mardix

