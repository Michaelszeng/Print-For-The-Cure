import smtplib, ssl
from .GoogleAPIKey import *

port = 465  # For SSL
sender_email = "printforthecure@gmail.com"

# Create a secure SSL context
def sendMessage(messageParam, subjectParam, recipient):
    receiver_email = recipient
    message = """\
    Subject: %s

%s""" % (subjectParam, messageParam)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("printforthecure@gmail.com", password)
        # TODO: Send email here
        server.sendmail(sender_email, receiver_email, message)

#test code
# sendMessage("HELOOOOOOO!!!!\n\nI AM MICHAEL!", "SUUUUBJEct!", "michaelszeng@gmail.com")
