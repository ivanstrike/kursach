import os
import logging
import traceback
from typing import Optional, List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import asyncio

from perfume_bot import PerfumeBot
from voice_processor import VoiceProcessor
from config import TELEGRAM_TOKEN, VOICE_CONFIG
from perfumes_data import PERFUMES_CATALOG

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramPerfumeBot:
    """Telegram-обёртка для PerfumeBot с поддержкой текста и голоса"""

    def __init__(self, token: str):
        self.token = token
        self.perfume_bot = PerfumeBot()
        self.voice_processor = VoiceProcessor(language=VOICE_CONFIG['language'])
        self.user_sessions = {}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Приветствие и краткая инструкция"""
        user_id = update.effective_user.id
        username = update.effective_user.first_name or "Друг"
        welcome_message = f"""
**Добро пожаловать в наш магазин элитных ароматов, {username}!**

Я АроматБот - ваш персональный консультант по парфюмерии!

**Что я умею:**
Подобрать идеальный аромат
Показать цены и акции
Помочь с оформлением заказа
Рассказать о специальных предложениях
Работать с голосовыми сообщениями

**Команды:**
/catalog - показать весь каталог
/prices - узнать цены
/help - справка

Просто напишите, что вас интересует, или отправьте голосовое сообщение! 🎤
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Справка по использованию"""
        help_text = """
**Справка по использованию:**

**Основные команды:**
• /start - начать работу
• /catalog - показать каталог ароматов
• /prices - посмотреть цены
• /stats - статистика бота

**Как пользоваться:**
1️ Просто опишите, что ищете: "Нужен мужской аромат для работы"
2️ Спросите о конкретном бренде: "Что есть от Chanel?"
3️ Уточните цены: "Сколько стоит Dior Sauvage?"
4️ Попросите рекомендацию: "Посоветуй что-то для свидания"

**Голосовые сообщения:**
Отправьте голосовое сообщение - я его распознаю и отвечу голосом!

**Покупка:**
Когда найдете подходящий аромат, напишите "купить" и я помогу оформить заказ!

Есть вопросы? Просто спрашивайте!
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def catalog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать каталог с кнопками покупки"""
        response = self.perfume_bot.process_message("покажи каталог", str(update.effective_user.id))
        found_perfumes = self._find_perfumes_in_response(response)
        keyboard = self._make_perfume_keyboard(found_perfumes)
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать цены с кнопками покупки"""
        response = self.perfume_bot.process_message("цены", str(update.effective_user.id))
        found_perfumes = self._find_perfumes_in_response(response)
        keyboard = self._make_perfume_keyboard(found_perfumes)
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика бота"""
        stats = self.perfume_bot.get_stats()
        total = sum(stats.values())
        if total > 0:
            stats_text = f"""
 **Статистика работы бота:**

Ответов по намерениям: {stats['intent']} ({stats['intent']/total*100:.1f}%)
Генеративных ответов: {stats['generate']} ({stats['generate']/total*100:.1f}%)
Неопознанных запросов: {stats['failure']} ({stats['failure']/total*100:.1f}%)

 Всего обработано сообщений: {total}
            """
        else:
            stats_text = "Статистика пока пуста. Начните диалог!"

        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений пользователя"""
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        response = self.perfume_bot.process_message(user_message, user_id)
        found_perfumes = self._find_perfumes_in_response(response)
        keyboard = self._make_perfume_keyboard(found_perfumes)
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
        logger.info(f"User {user_id}: {user_message}")
        logger.info(f"Bot response: {response[:100]}...")

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка голосовых сообщений пользователя"""
        user_id = str(update.effective_user.id)
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            voice = update.message.voice
            voice_file = await context.bot.get_file(voice.file_id)
            voice_data = await voice_file.download_as_bytearray()
            recognized_text, status = self.voice_processor.recognize_speech_from_audio(bytes(voice_data), input_format='ogg')
            if status != "success":
                await update.message.reply_text(f"{status}")
                return
            if not recognized_text:
                await update.message.reply_text("Не удалось распознать речь. Попробуйте еще раз.")
                return
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            response = self.perfume_bot.process_message(recognized_text, user_id)
            voice_response, voice_status = self.voice_processor.text_to_speech(response)
            found_perfumes = self._find_perfumes_in_response(response)
            keyboard = self._make_perfume_keyboard(found_perfumes, use_slug=True)
            if voice_status == "success" and voice_response:
                if keyboard:
                    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='record_voice')
                await context.bot.send_voice(
                    chat_id=update.effective_chat.id,
                    voice=voice_response
                )
            else:
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
                if voice_status != "success":
                    await update.message.reply_text(f" Не удалось сгенерировать голосовой ответ: {voice_status}")
            logger.info(f"Voice message from {user_id}: {recognized_text}")
        except Exception as e:
            logger.error(f"Error processing voice message: {e}\n{traceback.format_exc()}")
            await update.message.reply_text(
                "Произошла ошибка при обработке голосового сообщения. "
                "Попробуйте отправить текстовое сообщение."
            )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Глобальный обработчик ошибок"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.message:
            await update.message.reply_text(
                "Произошла техническая ошибка. Попробуйте еще раз через несколько секунд."
            )

    def run(self):
        """Запуск Telegram-бота"""
        if not self.token or self.token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            print("Ошибка: Не указан токен Telegram бота!")
            print("Получите токен у @BotFather и укажите его в config.py")
            return
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("catalog", self.catalog_command))
        app.add_handler(CommandHandler("prices", self.prices_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        app.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
        app.add_error_handler(self.error_handler)
        print("Бот запущен! Нажмите Ctrl+C для остановки.")
        print("Ссылка на бота: https://t.me/your_perfumer_bot")
        app.run_polling(drop_pending_updates=True)

    def _find_perfumes_in_response(self, response: str) -> List[Dict[str, Any]]:
        """Поиск упомянутых в ответе парфюмов по имени"""
        found = []
        for perfume in PERFUMES_CATALOG.values():
            if perfume['name'] in response:
                found.append(perfume)
        return found

    def _make_perfume_keyboard(self, perfumes: List[Dict[str, Any]], use_slug: bool = False) -> Optional[InlineKeyboardMarkup]:
        """Генерация клавиатуры с кнопками для покупки парфюма"""
        if not perfumes:
            return None
        buttons = []
        for perfume in perfumes:
            url = perfume['url']
            if use_slug:
                url = self._make_slug(perfume['brand'], perfume['name'])
                url = f"https://randewoo.ru/product/{url}"
            else:
                url = f"https://randewoo.ru/product/{url}"
            buttons.append(InlineKeyboardButton(
                f"Купить {perfume['name']}",
                url=url
            ))
        return InlineKeyboardMarkup([buttons])

    def _make_slug(self, brand: str, name: str) -> str:
        import re
        slug = f"{brand} {name}".lower()
        slug = re.sub(r'[^a-zA-Z0-9а-яА-Я ]', '', slug)
        slug = slug.replace('ё', 'e').replace('й', 'i')
        slug = slug.replace(' ', '-')
        return slug

def main():
    try:
        bot = TelegramPerfumeBot(TELEGRAM_TOKEN)
        bot.run()
    except KeyboardInterrupt:
        print("\nБот остановлен")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
