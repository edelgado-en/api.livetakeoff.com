import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class EmailUtil():
    
    def send_email(self, to_email, title, body):
        message = Mail(from_email='no-reply@livetakeoff.com',
                        to_emails=to_email,
                        subject=title,
                        html_content=body
                    )


        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            sg.send(message)
    
        except Exception as e:
            print(e.message)