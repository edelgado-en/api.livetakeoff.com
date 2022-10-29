from twilio.rest import Client
import os

class NotificationUtil():


    def send(self, message, to_number):
        client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))

        message = client.messages.create(
            body=message,
            from_=os.environ.get('TWILIO_NUMBER'),
            to=to_number
        )

        print(message.body)