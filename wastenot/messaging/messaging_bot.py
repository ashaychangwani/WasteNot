# Download the helper library from https://www.twilio.com/docs/python/install
import os
import twilio
from twilio.rest import Client


class messaging_bot():
    def __init__(self):
        self.account_sid = 'AC06326780c339640b4e3c84fc6561a867'
        self.auth_token = '3509ad9473cbacbaa3b30ad309885967'
        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, message, phone_number):
        message = self.client.messages \
            .create(
                body=message,
                from_='+15512965505',
                to='+1'+phone_number
            )
        if message is not None:
            return True
        return False



if __name__ == '__main__':
    bot = messaging_bot()
    bot.send_message('Hello','5519995873')