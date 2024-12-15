import requests
import schedule
import time
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from googlesearch import search

# Ваш токен API для Telegram-бота
TOKEN = '<TOKEN>'

# URL для получения новостей (например, с NewsAPI)
NEWS_API_URL = 'https://newsapi.org/v2/everything?q=technology&apiKey=<KEY>'

# Список указанных ресурсов
SOURCES = ['techcrunch', 'wired', 'theverge']

# Функция, которая будет вызываться при команде /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отправляем приветственное сообщение
    await update.message.reply_text('Привет! Я Helper. Отправьте мне сообщение.')

# Функция, которая будет повторять полученные сообщения
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отправляем полученное сообщение обратно пользователю
    await update.message.reply_text(update.message.text)

# Функция для получения и отправки свежих новостей
async def send_news(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    try:
        # Получаем новости с NewsAPI
        response = requests.get(NEWS_API_URL)
        news = response.json()

        # Проверяем, что запрос был успешным и есть статьи
        if news['status'] == 'ok' and news['articles']:
            # Берем первую статью из списка
            article = news['articles'][0]
            # Формируем сообщение с новостью
            message = f"Свежая новость:\n\n{article['title']}\n\n{article['description']}\n\nЧитать далее: {article['url']}"
            # Отправляем сообщение в чат
            await context.bot.send_message(chat_id=chat_id, text=message)
        else:
            # Отправляем сообщение об ошибке
            await context.bot.send_message(chat_id=chat_id, text="Не удалось получить новости. Пожалуйста, попробуйте позже.")
    except Exception as e:
        # Отправляем сообщение об ошибке
        await context.bot.send_message(chat_id=chat_id, text=f"Произошла ошибка: {str(e)}")

# Функция для поиска в интернете
async def search_web(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем текст запроса от пользователя
    query = update.message.text
    # Выполняем поиск в Google
    results = search(query, num_results=5)
    # Формируем сообщение с результатами поиска
    message = "Результаты поиска:\n\n"
    for result in results:
        message += f"{result}\n\n"
    # Отправляем сообщение с результатами поиска
    await update.message.reply_text(message)

# Функция для обработки сообщений и выполнения поиска, если есть ключевые слова
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем текст сообщения
    text = update.message.text.lower()
    # Проверяем наличие ключевых слов
    if re.search(r'\b(новости|news|события)\b', text):
        # Вызываем функцию отправки новостей с передачей chat_id
        await send_news(context, update.message.chat_id)
    else:
        # Вызываем функцию эхо, если ключевых слов нет
        await echo(update, context)

def main() -> None:
    # Создаем ApplicationBuilder и передаем ему токен вашего бота
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Планируем отправку новостей каждый час
    # Замените 'YOUR_CHAT_ID' на идентификатор чата, в который вы хотите отправлять новости
    schedule.every().hour.do(lambda: application.job_queue.run_once(send_news, 0, chat_id=YOUR_CHAT_ID))

    # Запускаем бота
    application.run_polling()

    # Запускаем планировщик
    while True:
        schedule.run_pending()
        time.sleep(1)

# Проверяем, запущен ли скрипт напрямую
if __name__ == '__main__':
    main()

