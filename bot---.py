import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
from config import BOT_TOKEN, AGENCY_NAME, AGENT_NAME, REALTOR_NAME, DEMO_PROPERTY, ADMIN_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
GREETING, DEAL_TYPE, BUDGET, MORTGAGE, URGENCY, VIEWING_TIME, FINISH = range(7)

# Хранилище данных пользователей
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога с приветствием"""
    user = update.effective_user
    if not user:
        return ConversationHandler.END
    
    user_data[user.id] = {
        'name': user.first_name or "Пользователь",
        'username': user.username or "unknown",
        'phone': None
    }
    
    welcome_text = f"""Добрый день! Меня зовут {AGENT_NAME}, я виртуальный помощник агентства {AGENCY_NAME}. 

Рад помочь с квартирой на {DEMO_PROPERTY['address']}!

🏠 {DEMO_PROPERTY['description']}
💰 Цена: {DEMO_PROPERTY['price']}
📐 Площадь: {DEMO_PROPERTY['area']}
🛏 Комнат: {DEMO_PROPERTY['rooms']}
🏢 Этаж: {DEMO_PROPERTY['floor']}

Чтобы я мог сориентировать вас и риелтора наилучшим образом, ответьте, пожалуйста, на несколько вопросов.

Подскажите, вас интересует покупка или долгосрочная аренда?"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Покупка", callback_data="purchase")],
        [InlineKeyboardButton("🏡 Аренда", callback_data="rent")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return DEAL_TYPE

async def deal_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора типа сделки"""
    query = update.callback_query
    if not query or not query.data:
        return ConversationHandler.END
    
    await query.answer()
    
    user_id = query.from_user.id
    deal_type = query.data
    user_data[user_id]['deal_type'] = "Покупка" if deal_type == "purchase" else "Аренда"
    
    budget_text = "Отлично! Какой у вас бюджет на покупку?"
    if deal_type == "rent":
        budget_text = "Отлично! Какой у вас бюджет на аренду?"
    
    keyboard = [
        [InlineKeyboardButton("До 10 млн", callback_data="budget_10")],
        [InlineKeyboardButton("10-15 млн", callback_data="budget_15")],
        [InlineKeyboardButton("15-20 млн", callback_data="budget_20")],
        [InlineKeyboardButton("Более 20 млн", callback_data="budget_20+")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=budget_text, reply_markup=reply_markup)
    return BUDGET

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора бюджета"""
    query = update.callback_query
    if not query or not query.data:
        return ConversationHandler.END
    await query.answer()
    
    user_id = query.from_user.id
    budget_map = {
        "budget_10": "До 10 млн",
        "budget_15": "10-15 млн", 
        "budget_20": "15-20 млн",
        "budget_20+": "Более 20 млн"
    }
    user_data[user_id]['budget'] = budget_map[query.data]
    
    mortgage_text = "Планируете использовать ипотеку? Уже есть одобрение от банка?"
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, ипотека, одобрение есть", callback_data="mortgage_yes")],
        [InlineKeyboardButton("❌ Нет, наличные", callback_data="mortgage_no")],
        [InlineKeyboardButton("🤔 Планирую оформить", callback_data="mortgage_plan")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=mortgage_text, reply_markup=reply_markup)
    return MORTGAGE

async def mortgage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка вопроса об ипотеке"""
    query = update.callback_query
    if not query or not query.data:
        return ConversationHandler.END
    await query.answer()
    
    user_id = query.from_user.id
    mortgage_map = {
        "mortgage_yes": "Да, ипотека, одобрение есть",
        "mortgage_no": "Нет, наличные",
        "mortgage_plan": "Планирую оформить"
    }
    user_data[user_id]['mortgage'] = mortgage_map[query.data]
    
    urgency_text = "Как срочно планируете переезд?"
    
    keyboard = [
        [InlineKeyboardButton("🚨 Очень срочно (1-2 недели)", callback_data="urgency_1")],
        [InlineKeyboardButton("⚡ В течение месяца", callback_data="urgency_2")],
        [InlineKeyboardButton("📅 В течение 3 месяцев", callback_data="urgency_3")],
        [InlineKeyboardButton("⏰ Не спешу", callback_data="urgency_4")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=urgency_text, reply_markup=reply_markup)
    return URGENCY

async def urgency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка вопроса о срочности"""
    query = update.callback_query
    if not query or not query.data:
        return ConversationHandler.END
    await query.answer()
    
    user_id = query.from_user.id
    urgency_map = {
        "urgency_1": "Очень срочно (1-2 недели)",
        "urgency_2": "В течение месяца",
        "urgency_3": "В течение 3 месяцев", 
        "urgency_4": "Не спешу"
    }
    user_data[user_id]['urgency'] = urgency_map[query.data]
    
    viewing_text = "Когда вам было бы удобно посмотреть объект?"
    
    keyboard = [
        [InlineKeyboardButton("📅 В эти выходные", callback_data="viewing_weekend")],
        [InlineKeyboardButton("🌅 В будни вечером", callback_data="viewing_evening")],
        [InlineKeyboardButton("☀️ В будни днем", callback_data="viewing_day")],
        [InlineKeyboardButton("📞 Свяжитесь для уточнения", callback_data="viewing_call")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=viewing_text, reply_markup=reply_markup)
    return VIEWING_TIME

async def viewing_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка времени просмотра и завершение диалога"""
    query = update.callback_query
    if not query or not query.data:
        return ConversationHandler.END
    await query.answer()
    
    user_id = query.from_user.id
    viewing_map = {
        "viewing_weekend": "В эти выходные",
        "viewing_evening": "В будни вечером",
        "viewing_day": "В будни днем",
        "viewing_call": "Свяжитесь для уточнения"
    }
    user_data[user_id]['viewing_time'] = viewing_map[query.data]
    
    # Формируем карточку лида
    lead_card = format_lead_card(user_id)
    
    # Отправляем лида риелтору
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=lead_card,
            parse_mode='HTML'
        )
    
    # Завершаем диалог с клиентом
    finish_text = f"""Спасибо за ответы! 

Я передал всю информацию нашему специалисту по этому объекту, {REALTOR_NAME}. 

Он свяжется с вами в течение часа, чтобы договориться о времени показа.

📞 Контакт: +7 (495) 123-45-67
📧 Email: info@дом-эксперт.рф

До встречи! 👋"""
    
    await query.edit_message_text(text=finish_text)
    return ConversationHandler.END

def format_lead_card(user_id: int) -> str:
    """Форматирование карточки лида для риелтора"""
    data = user_data[user_id]
    
    card = f"""🔥 <b>НОВЫЙ ГОРЯЧИЙ ЛИД!</b>

🏠 <b>Объект:</b> {DEMO_PROPERTY['address']}
👤 <b>Клиент:</b> {data['name']} (@{data['username']})
💰 <b>Тип:</b> {data['deal_type']}
💵 <b>Бюджет:</b> {data['budget']}
🏦 <b>Ипотека:</b> {data['mortgage']}
⏰ <b>Срочность:</b> {data['urgency']}
📅 <b>Готовность к показу:</b> {data['viewing_time']}

📱 <b>Контакт:</b> @{data['username']}

<i>Автоматически квалифицирован ботом {AGENT_NAME}</i>"""
    
    return card

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда помощи"""
    help_text = """🤖 <b>Демо-бот для квалификации клиентов недвижимости</b>

Этот бот автоматически проводит первичную квалификацию клиентов и передает информацию риелтору.

<b>Как использовать:</b>
1. Начните диалог командой /start
2. Ответьте на вопросы бота
3. Получите квалифицированного лида

<b>Команды:</b>
/start - Начать квалификацию
/help - Показать эту справку

<i>Демо-версия для показа потенциальным клиентам</i>"""
    
    if update.message:
        await update.message.reply_text(help_text, parse_mode='HTML')

def main() -> None:
    """Запуск бота"""
    if not BOT_TOKEN:
        print("❌ Ошибка: Не указан токен бота в переменной окружения BOT_TOKEN")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Создаем обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DEAL_TYPE: [CallbackQueryHandler(deal_type_handler)],
            BUDGET: [CallbackQueryHandler(budget_handler)],
            MORTGAGE: [CallbackQueryHandler(mortgage_handler)],
            URGENCY: [CallbackQueryHandler(urgency_handler)],
            VIEWING_TIME: [CallbackQueryHandler(viewing_time_handler)],
        },
        fallbacks=[CommandHandler("help", help_command)],
    )
    
    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 