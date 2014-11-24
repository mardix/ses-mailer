"""
SES Mailer Test


Create a file test_config.py and add the following

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
EMAIL_SENDER = ""
EMAIL_RECIPIENT = ""

"""

import unittest

from jinja2 import Template as jinjaTemplate

from ses_mailer import Mail, TemplateMail, Template
import test_config


class TestTemplate(unittest.TestCase):

    def setUp(self):
        templateMap = {
            "test.txt": """
            {% block subject %}I'm subject{% endblock %}
            {% block body %}How are you {{name}}?{% endblock %}
            """,
            "contact.txt": "Contact us at {{email}}"
        }
        file_ext = ".txt"
        self.context_name = "Jones"
        self.r_body = "How are you %s?" % self.context_name

        self.T = Template(template_map=templateMap, file_extension=file_ext)

    def test_file_extension(self):
        self.assertNotEqual(self.T._add_file_extension("test"), "test")
        self.assertEqual(self.T._add_file_extension("test"), "test.txt")
        self.assertEqual(self.T._add_file_extension("nose.txt"), "nose.txt")

    def test_get_template(self):
        self.assertIsInstance(self.T._get_template("test"), jinjaTemplate)

    def test_render_blocks(self):
        self.assertIsInstance(self.T.render_blocks("test"), dict)

    def test_rendered_blocks(self):
        blocks = self.T.render_blocks("test")
        self.assertTrue("subject" in blocks)
        self.assertTrue("body" in blocks)
        self.assertFalse("largo" in blocks)

    def test_render(self):
        self.assertEqual(self.T.render("test", "body", name=self.context_name), self.r_body)

class TestMail(unittest.TestCase):
    def setUp(self):
        self.MAIL = Mail(aws_secret_access_key=test_config.AWS_SECRET_ACCESS_KEY,
                              aws_access_key_id=test_config.AWS_ACCESS_KEY_ID,
                              sender=test_config.EMAIL_SENDER)

    def test_get_sender(self):
        self.assertIsInstance(self.MAIL._get_sender(("Name", "name@yahoo.com")), tuple)
        self.assertEqual(self.MAIL._get_sender(("Name", "name@yahoo.com"))[0], "Name <name@yahoo.com>")

    def test_send(self):
        r = self.MAIL.send(test_config.EMAIL_RECIPIENT, subject="Test", body="TEST BODY")
        self.assertIsNotNone(r)


class TestTemplateMail(unittest.TestCase):
    def setUp(self):

        templateMap = {
            "welcome.txt": """
            {% block subject %}I'm subject{% endblock %}
            {% block body %}How are you {{name}}?{% endblock %}
            """,
            "no_blocks.txt": "Contact us at {{email}}",
            "no_subject.txt": """
            {% block body %}How are you {{name}}?{% endblock %}
            """,
            "no_body.txt": """
            {% block subject %}I'm subject{% endblock %}
            """
        }

        self.TMAIL = TemplateMail(aws_secret_access_key=test_config.AWS_SECRET_ACCESS_KEY,
                              aws_access_key_id=test_config.AWS_ACCESS_KEY_ID,
                              sender=test_config.EMAIL_SENDER,
                              template_map=templateMap,
                              file_extension=".txt")

    def test_send_bad(self):
        with self.assertRaises(AttributeError):
            self.TMAIL.send("no_blocks", to=test_config.EMAIL_RECIPIENT)
            self.TMAIL.send("no_subject", to=test_config.EMAIL_RECIPIENT)
            self.TMAIL.send("no_body", to=test_config.EMAIL_RECIPIENT)

    def test_send_welcome(self):
        self.assertIsNotNone(self.TMAIL.send("welcome", to=test_config.EMAIL_RECIPIENT, name="Mardix"))