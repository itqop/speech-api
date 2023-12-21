import aiohttp
import json
from langdetect import detect
import re

class Translate:
    def __init__(self, api_url="https://libretranslate.com/translate"):
        self.api_url = api_url

    async def translate_text(self, text, source_lang, target_lang="ru"):
        params = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=params) as response:
                data = await response.text()

        translation = json.loads(data)[0]['translatedText']
        return translation

    async def preprocess_text(self, text):
        text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
        text = re.sub(r'[^A-Za-z0-9А-Яа-я\s]', '', text)  # Remove special characters
        return text

    async def postprocess_text(self, text):
        return f"[Translated]: {text}"

    async def batch_translate_text(self, text_list, source_lang, target_lang="ru"):
        translations = []

        for text in text_list:
            preprocessed_text = self.preprocess_text(text)
            translated_text = await self.translate_text(preprocessed_text, source_lang, target_lang)
            postprocessed_text = self.postprocess_text(translated_text)
            translations.append(postprocessed_text)

        return translations

    async def detect_language(self, text):
        detected_lang = detect(text)
        return detected_lang
