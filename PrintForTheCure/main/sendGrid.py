from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



def sendMessage(messageParam, subjectParam, recipient):
    message = Mail(from_email='printforthecure@printforthecure.com',
    to_emails=recipient,
    subject=subjectParam,
    html_content=messageParam)
    #MESSAGE HERE
    try:
        sg = SendGridAPIClient()
        response = sg.send(message)
    except Exception as e:
        print(e.message)

# sendMessage("Very long message wow gggggggggggggggggggggggggggg %s gggggggggggggggggggggggggggggg<br />adsfadfadfadf<br /><br />regsfgtgefvcefwrefvscewrfvd" % "test", "sub", "michaelszeng@gmail.com")
