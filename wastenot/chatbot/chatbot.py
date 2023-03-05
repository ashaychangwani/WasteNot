"""
ChatBot class file
"""

import re

import backoff
import openai
from openai.error import RateLimitError, ServiceUnavailableError


class ChatBot:
    """
    ChatBot
    """

    openai.api_key = "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"
    start_sequence = "\nQ:"
    restart_sequence = "\nA: "
    success_string = "all the information I need"
    chats = []

    def __init__(self):
        self.chats = []
        self.chats.append(
            "Hi, if you'd like to save the planet bite-by-bite, "
            "please let me know details about the food you'd like to donate!"
        )

        with open("prompt.txt", "r") as file:
            self.base_prompt = file.read()

    def build_prompt(self) -> str:
        """
        Build the prompt for the OpenAI API
        :return: Prompt string
        """

        formatted_strings = []
        for i, string in enumerate(self.chats):
            if i % 2 == 0:
                formatted_strings.append(self.start_sequence + string)
            else:
                formatted_strings.append(self.restart_sequence + string)

        return self.base_prompt + ("\n".join(formatted_strings)) + self.start_sequence

    @backoff.on_exception(backoff.expo, (RateLimitError, ServiceUnavailableError))
    def getResponse(self, query: str) -> str:
        """
        Get the response from the OpenAI API
        :param query: Query string
        :return: Response string
        """

        self.chats.append(query)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=self.build_prompt(),
            temperature=0.7,
            max_tokens=461,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["A:"],
        )
        response = response.choices[0].text.strip()
        self.check_if_completed(response)
        self.chats.append(response)
        return response

    def check_if_completed(self, response):
        """
        Check if the response contains the success string
        :param response: Response string
        :return: None
        """
        if self.success_string in response:
            pattern = r"([A-Za-z ]+): ([A-Za-z0-9# ]+)"
            matches = re.findall(pattern, response)
            variables = {}
            for match in matches:
                variables[match[0]] = match[1]

            type_of_food = variables.get("Type of food", "N/A")
            weight = variables.get("Weight", "N/A")
            street = variables.get("Street Address", "N/A")
            apt = variables.get("Apartment", "N/A")
            city = variables.get("City", "N/A")
            state = variables.get("State", "N/A")
            zip_code = variables.get("Zip", "N/A")
            phone = variables.get("Phone Number", "N/A")
            na_count = sum(
                value == "N/A"
                for value in [
                    type_of_food,
                    weight,
                    street,
                    apt,
                    city,
                    state,
                    zip_code,
                    phone,
                ]
            )
            if na_count < 3:
                self.addLocationToDB(
                    type_of_food, weight, street, apt, city, state, zip_code, phone
                )

    def addLocationToDB(
        self, type_of_food, weight, street, apt, city, state, zip_code, phone
    ):
        # TODO: add to database
        print("Type of Food:", type_of_food)
        print("Weight:", weight)
        print("Street:", street)
        print("Apt:", apt)
        print("City:", city)
        print("State:", state)
        print("Zip:", zip_code)
        print("Phone:", phone)


if __name__ == "__main__":
    __bot = ChatBot()
    __query = "hi"
    while __query != "":
        __query = input("A: ")
        if __query != "":
            print(__bot.getResponse(__query))
