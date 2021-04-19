"""
SES Mailer Test


Create a file test_config.py and add the following

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = ""
EMAIL_SENDER = ""
EMAIL_RECIPIENT = ""

"""

import pytest
from jinja2 import Template as jinjaTemplate
from ses_mailer import Mail, Template
import test_config


templateMap = {
    "test": """
    {% block subject %}I'm subject{% endblock %}
    {% block body %}How are you {{name}}?{% endblock %}
    """,
    "contact": "Contact us at {{email}}",
    "welcome": """
    {% block subject %}I'm subject{% endblock %}
    {% block body %}How are you {{name}}?{% endblock %}
    """,
    "no_blocks": "Contact us at {{email}}",
    "no_subject": """
    {% block body %}How are you {{name}}?{% endblock %}
    """,
    "no_body": """
    {% block subject %}I'm subject{% endblock %}
    """    
}
template = Template(templateMap)

def test_template_is_jinja():
    assert isinstance(template._get_template("test"), jinjaTemplate)

def test_template_block():
    assert isinstance(template.render_blocks("test"), dict)

def test_template_rendered_block():
    blocks = template.render_blocks("test")
    assert "subject" in blocks
    assert "body" in blocks
    assert "largo" not in "blocks"

def test_template_render():
    name = "Jones"
    line = "How are you %s?" % name
    assert line == template.render("test", "body", name=name)

##----

mail = Mail(aws_secret_access_key=test_config.AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=test_config.AWS_ACCESS_KEY_ID,
            region=test_config.AWS_REGION,
            sender=test_config.EMAIL_SENDER,
            template=templateMap)

def test_mail_get_sender():
    assert isinstance(mail._get_sender(("Name", "name@yahoo.com")), tuple)
    assert "Name <name@yahoo.com>" == mail._get_sender(("Name", "name@yahoo.com"))[0]

def test_mail_send():
    r = mail.send(test_config.EMAIL_RECIPIENT, subject="Test", body="TEST BODY")
    assert r is not None

def test_mail_send_change_reply_to():
    r = mail.send(test_config.EMAIL_RECIPIENT, subject="Test With Reply To", reply_to="nola@nola.com", body="TEST BODY - reply to nola@nola.com")
    assert r is not None

def test_mail_send_template_error():
    with pytest.raises(AttributeError):
        mail.send_template("no_blocks", to=test_config.EMAIL_RECIPIENT)
        mail.send_template("no_subject", to=test_config.EMAIL_RECIPIENT)
        mail.send_template("no_body", to=test_config.EMAIL_RECIPIENT)


def test_send_template_welcome():
    r = mail.send_template("welcome", to=test_config.EMAIL_RECIPIENT, name="Mardix")
    assert r is not None

