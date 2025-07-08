import os
from dotenv import load_dotenv

load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '')

# Настройки агентства
AGENCY_NAME = "Агентство недвижимости 'Дом-Эксперт'"
AGENT_NAME = "Анна"
REALTOR_NAME = "Михаил Петров"

# Объект недвижимости для демо
DEMO_PROPERTY = {
    "address": "ул. Ленина, 5",
    "price": "12 500 000 ₽",
    "area": "75 м²",
    "rooms": "3",
    "floor": "5/9",
    "description": "Современная 3-комнатная квартира в центре города с ремонтом под ключ"
} 