import os
from dotenv import load_dotenv

load_dotenv()

Bot_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

ChatGPT_TOKEN = os.getenv('CHATGPT_TOKEN')

# Proxy settings (только для openai, не устанавливаем глобально)
# OPENAI_PROXY = 'http://18.199.183.77:49232' 