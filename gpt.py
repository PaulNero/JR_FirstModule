import openai
import httpx as httpx


class ChatGptService:
    message_list: list = None

    def __init__(self, token):
        token = "sk-proj-" + token[:3:-1] if token.startswith('gpt:') else token
        openai.api_key = token
        # Настройка прокси для openai
        openai.proxy = "http://18.199.183.77:49232"
        self.message_list = []

    def send_message_list(self) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # gpt-4o,  gpt-4-turbo,    gpt-3.5-turbo,  GPT-4o mini
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        message = completion.choices[0].message
        self.message_list.append(message)
        return message['content']

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return self.send_message_list()

    def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return self.send_message_list()
