"""
SESMailer2
"""

from setuptools import setup, find_packages

import ses_mailer

PACKAGE = ses_mailer

setup(
    name=PACKAGE.__NAME__,
    version=PACKAGE.__version__,
    license=PACKAGE.__license__,
    author=PACKAGE.__author__,
    author_email='mardix@github.com',
    description="A simple module to send email via AWS SES",
    long_description=PACKAGE.__doc__,
    url='http://github.com/MarSoft/ses-mailer-2/',
    download_url='http://github.com/MarSoft/ses-mailer-2/tarball/master',
    py_modules=['ses_mailer'],
    include_package_data=True,
    install_requires=[
        "boto",
        "jinja2"
    ],

    keywords=['email',
              'flask',
              'aws ses',
              'amazon',
              'ses',
              'mailer',
              'jinja2',
              'template email'],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(exclude=["test_config.py"]),
    zip_safe=False
)
