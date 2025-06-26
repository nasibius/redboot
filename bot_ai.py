#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re
import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import BadRequest
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "!!!PASTE YOUR TELEGRAM TOKEN ONLY HERE!!!")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "!!!PASTE YOUR API KEY ONLY HERE!!!")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- PROMPT ---
SYSTEM_PROMPT = """
Ты — элитный ИИ-ассистент по кибербезопасности «RedBoot».
Твоя задача — давать экспертные, краткие и понятные ответы.

**Правила форматирования:**
- Используй форматирование, чтобы сделать текст читаемым.
- **Жирным** выделяй заголовки и ключевые термины.
- `Кодом` выделяй команды, пути к файлам и примеры кода.
- Для списков используй дефис `-`.
- Используй релевантные смайлики (🛡️, 🔒, 💡, ⚠️, ✅, 🚨) для наглядности.
"""

# --- MARKDOWN TO HTML ---
def translate_markdown_to_html(text: str) -> str:
    """
    Переводит основные элементы Markdown в HTML-теги.
    """
    # Сначала обрабатываем блоки кода ```...```
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    # Затем жирный текст **...**
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # И встроенный код `...`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text

def sanitize_telegram_html(text: str) -> str:
    """Надежно экранирует HTML, оставляя разрешенные Telegram теги нетронутыми."""
    allowed_tags = ['b', 'i', 'u', 's', 'a', 'code', 'pre']
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    for tag in allowed_tags:
        text = text.replace(f'&lt;{tag}&gt;', f'<{tag}>').replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    text = text.replace(f'&lt;pre&gt;', '<pre>').replace(f'&lt;/pre&gt;', '</pre>')
    return text

def configure_gemini():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        safety_settings = { HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, }
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT, safety_settings=safety_settings)
        return model
    except Exception as e:
        logger.error(f"Ошибка конфигурации Gemini AI: {e}")
        return None

# --- ФУНКЦИИ-ОБРАБОТЧИКИ TELEGRAM ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    # При старте очищаем историю, чтобы начать новый диалог
    context.chat_data.clear()
    await update.message.reply_html(f"👋 Приветствую, {user.mention_html()}!\n\nЯ — ваш персональный ассистент по кибербезопасности <b>RedBoot</b>. Наша беседа будет сохраняться в рамках этой сессии. Чтобы начать заново, используйте /clear.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html("<b>Как пользоваться ботом:</b>\nПросто напишите ваш вопрос в чат.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает сообщения, используя и обновляя память диалога."""
    user_message = update.message.text
    logger.info(f"Получено сообщение от {update.effective_user.username}: {user_message}")
    
    processing_message = await update.message.reply_text("🧠...")

    try:
        # --- ЛОГИКА ПАМЯТИ: НАЧАЛО ---
        # 1. Получаем историю из памяти чата. Если ее нет, создаем пустой список.
        history = context.chat_data.get('history', [])
        
        # 2. Формируем сообщение для Gemini, включая всю предыдущую историю.
        messages_for_gemini = history + [{'role': 'user', 'parts': [user_message]}]
        
        # 3. Отправляем в Gemini весь контекст
        chat_model = genai.GenerativeModel('gemini-1.5-flash')
        stream_response = chat_model.generate_content(messages_for_gemini, stream=True)

        # --- ЛОГИКА ПАМЯТИ: КОНЕЦ ---
        full_text = ""
        last_edit_time = asyncio.get_event_loop().time()
        
        for chunk in stream_response:
            if chunk.text:
                full_text += chunk.text
                current_time = asyncio.get_event_loop().time()
                if current_time - last_edit_time > 0.6:
                    translated_text = translate_markdown_to_html(full_text)
                    sanitized_text = sanitize_telegram_html(f"{translated_text} ✍️")
                    try:
                        await processing_message.edit_text(text=sanitized_text, parse_mode=ParseMode.HTML)
                        last_edit_time = current_time
                    except BadRequest as e:
                        if "Message is not modified" not in str(e):
                            logger.warning(f"Не удалось обновить сообщение (некритично): {e}")

        # Финальная обработка всего текста
        final_translated_text = translate_markdown_to_html(full_text)
        final_sanitized_text = sanitize_telegram_html(final_translated_text)
        
        if processing_message.text != final_sanitized_text:
             await processing_message.edit_text(text=final_sanitized_text, parse_mode=ParseMode.HTML)
             
        # --- ОБНОВЛЕНИЕ ПАМЯТИ: НАЧАЛО ---
        # 4. Добавляем вопрос пользователя и ответ бота в историю.
        history.append({'role': 'user', 'parts': [user_message]})
        history.append({'role': 'model', 'parts': [full_text]})
        
        # 5. Ограничиваем историю, чтобы она не росла бесконечно (сейвим последние 50 сообщений).
        if len(history) > 50:
            history = history[-50:]
            
        # 6. Сохраняем обновленную историю обратно в память чата.
        context.chat_data['history'] = history
        # --- ОБНОВЛЕНИЕ ПАМЯТИ: КОНЕЦ ---

    except Exception as e:
        logger.error(f"Произошла критическая ошибка: {e}", exc_info=True)
        await processing_message.edit_text("Извините, произошла внутренняя ошибка.")
# --- НОВАЯ ФУНКЦИЯ ДЛЯ ОЧИСТКИ ПАМЯТИ ---
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очищает историю диалога."""
    context.chat_data.clear()
    await update.message.reply_html("🧹 Память диалога очищена. Начинаем с чистого листа!")

# --- ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА БОТА ---

def main() -> None:
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY or "СЮДА" in TELEGRAM_TOKEN:
        logger.error("ОШИБКА: Токены Telegram или Gemini не установлены.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запускается в финальном режиме с 'переводчиком'...")
    application.run_polling()


if __name__ == "__main__":
    gemini_model = configure_gemini()
    if gemini_model:
        main()
    else:
        logger.critical("Не удалось инициализировать модель Gemini. Бот не может быть запущен.")
