"""
Messaging service
"""

from twilio.rest import Client


class MessagingBot:
    """
    Messaging bot class
    """

    def __init__(self):
        self.account_sid = "AC06326780c339640b4e3c84fc6561a867"
        self.auth_token = "3509ad9473cbacbaa3b30ad309885967"
        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, message, phone_number):
        """
        Send a message to a phone number
        :param message: Message to send
        :param phone_number: Phone number to send to
        :return: True if message was sent, False otherwise
        """

        message = self.client.messages.create(
            body=message, from_="+15512965505", to="+1" + phone_number
        )
        if message is not None:
            return True
        return False


if __name__ == "__main__":
    bot = MessagingBot()
    bot.send_message("Hello", "5519995873")
