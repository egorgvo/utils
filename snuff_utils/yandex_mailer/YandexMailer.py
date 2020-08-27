#!/usr/bin/env python2.7
# coding=utf-8

from os.path import basename
from smtplib import SMTP_SSL
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import YANDEX_SMTP_SERVER


class YandexMailer():
    """
    Класс, реализующий библиотеку для отправки электронной почты с помощью яндекс
    """
    @classmethod
    def send_mail(cls, sender_email, password, recipients_emails, title, body=None, attachment=None):
        # Преобразуем recipients_emails к списку
        recipients_emails = recipients_emails.split(',') \
            if isinstance(recipients_emails, str) else recipients_emails

        # Формируем сообщение
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ','.join(recipients_emails)
        msg['Subject'] = title
        if body and isinstance(body, MIMEText):
            msg.attach(body)
        elif body:
            msg.attach(cls.form_text_body(body))
        if attachment:
            msg.attach(attachment)

        # Отправка
        smtp = SMTP_SSL(YANDEX_SMTP_SERVER)
        smtp.connect(YANDEX_SMTP_SERVER)
        smtp.login(sender_email, password)
        smtp.sendmail(sender_email, recipients_emails, msg.as_string())
        smtp.quit()

    @staticmethod
    def form_html_body(html):
        return MIMEText(html, 'html')

    @staticmethod
    def form_text_body(text):
        return MIMEText(text, 'plain')

    @staticmethod
    def form_attachment(filename, name=''):
        if not name:
            name = basename(filename)
        # Формируем вложение
        attachment = MIMEBase('application', "octet-stream")
        attachment.set_payload(open(filename, "rb").read())
        encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=name)
        return attachment
