from moviepy.editor import AudioFileClip

from telegram import File, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    filters,
    MessageHandler,
    Application,
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
)

from googletrans import Translator

import speech_recognition as sr

from credential_reader import Credentials

from chat_gpt import GptWrapper, BhashiniWrapper

import os


class Recog:
    def __init__(self) -> None:
        self.r = sr.Recognizer()

    def convert(self, filename):
        with sr.AudioFile(filename) as source:
            audio1 = self.r.record(source)

        text = self.r.recognize_google(audio1, language="auto")

        return text


class Telebot:
    def __init__(self) -> None:
        self.credentials = Credentials()

        self.chat_langauges = {}

        self.recog = Recog()

        self.translator = Translator()

        self.gpt = GptWrapper()

        self.bhashini = BhashiniWrapper()

        self.languages = {
            "English": "en",
            "Hindi": "hi",
            "Kannada": "kn",
            "Telugu": "te",
            "Tamil": "ta",
            "Bengali": "bn",
            "Malayalam": "ml",
            "Marathi": "mr",
        }

        self.token = self.credentials.get_telegram_token()

    async def options(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends a message with three inline buttons attached."""

        keyboard = [
            InlineKeyboardButton(lang, callback_data=lang)
            for lang in self.languages.keys()
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[x] for x in keyboard])

        await update.message.reply_text("Please choose:", reply_markup=keyboard)

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        self.chat_langauges[update.effective_chat.id] = query.data

        await query.edit_message_text(text=f"Selected option: {query.data}")

    async def get_response(self, file: File):
        path = await file.download_to_drive()

        clip = AudioFileClip(str(path))

        name = str(path).split(".")[0]

        clip.write_audiofile(name + ".wav")

        text = self.recog.convert(name + ".wav")

        os.remove(path)
        os.remove(name + ".wav")

        return text, name

    async def voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        f = await update.message.voice.get_file()

        text, name = await self.get_response(f)

        name = name + "_resp"

        if update.effective_chat.id in self.chat_langauges.keys():
            full_lan = self.chat_langauges[update.effective_chat.id]
            lan_code = self.languages[full_lan]

            tt = self.translator.translate(text, src=lan_code, dest="en")

            rcvd_local = self.bhashini.convert_response(tt.text, full_lan, lan_code)

            resp_text = f"Recieved: \n{rcvd_local}"

            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=resp_text
            )

            res = self.gpt.chatbot(tt.text)

            response_from_gpt_in_local = self.bhashini.convert_response(
                res, full_lan, lan_code, name + ".wav"
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=response_from_gpt_in_local
            )

            with open(name + ".wav", "rb") as f:
                await context.bot.send_voice(chat_id=update.effective_chat.id, voice=f)

            os.remove(name + ".wav")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please use /start to select a language",
            )

    def start(self):
        application = Application.builder().token(self.token).build()

        voice_handler = MessageHandler(filters.VOICE, self.voice)

        application.add_handler(CommandHandler("start", self.options))
        application.add_handler(CallbackQueryHandler(self.button))

        application.add_handler(voice_handler)
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    tb = Telebot()
    tb.start()
