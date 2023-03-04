import os
import openai
import backoff
import re

from openai.error import RateLimitError, ServiceUnavailableError

class ChatBot:
    openai.api_key = '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'
    start_sequence = "\nQ:"
    restart_sequence = "\nA: "
    success_string = 'all the information I need'
    chats = []
    def __init__(self):
        self.chats = []
        self.chats.append("Hi, if you'd like to save the planet bite-by-bite, please let me know details about the food you'd like to donate!")
        
        with open('prompt.txt', 'r') as file:
            self.base_prompt = file.read()
            
    def build_prompt(self):
        formatted_strings = []
        for i, string in enumerate(self.chats):
            if i % 2 == 0:
                formatted_strings.append(self.start_sequence + string)
            else:
                formatted_strings.append(self.restart_sequence + string)
        return self.base_prompt + ("\n".join(formatted_strings)) + self.start_sequence
    
    @backoff.on_exception(backoff.expo, (RateLimitError, ServiceUnavailableError))
    def getResponse(self, query):
        self.chats.append(query)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=self.build_prompt(), 
            temperature=0.7,
            max_tokens=461,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["A:"]
            )
        response = response.choices[0].text.strip()
        self.checkIfCompleted(response)
        self.chats.append(response)
        return response
        
    def checkIfCompleted(self, response):
        if self.success_string in response:
            pattern = r'([A-Za-z ]+): ([A-Za-z0-9# ]+)'
            matches = re.findall(pattern, response)
            variables = {}
            for match in matches:
                variables[match[0]] = match[1]
            
            type_of_food = variables.get('Type of food', 'N/A')
            weight = variables.get('Weight', 'N/A')
            street = variables.get('Street Address', 'N/A')
            apt = variables.get('Apartment', 'N/A')
            city = variables.get('City', 'N/A')
            state = variables.get('State', 'N/A')
            zip_code = variables.get('Zip', 'N/A')
            na_count = sum(value == 'N/A' for value in [type_of_food, weight, street, apt, city, state, zip_code])
            if na_count < 3:
                self.addLocationToDB(type_of_food, weight, street, apt, city, state, zip_code)
        
    def addLocationToDB(self, type_of_food, weight, street, apt, city, state, zip_code):
        # TODO: add to database
        print('Type of Food:', type_of_food)
        print('Weight:', weight)
        print('Street:', street)
        print('Apt:', apt)
        print('City:', city)
        print('State:', state)
        print('Zip:', zip_code)
        
if __name__ == "__main__":
    bot = ChatBot()
    query = "hi"
    while (query != ''):
        query = input('A: ')
        if (query != ''):
            print(bot.getResponse(query))





