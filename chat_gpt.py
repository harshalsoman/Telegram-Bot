import os
import io

import requests

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from pydub import AudioSegment

from credential_reader import Credentials


class GptWrapper:
    def __init__(self) -> None:
        os.environ["OPENAI_API_KEY"] = Credentials().get_openai_key()

        self.llm = ChatOpenAI(
            temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=512
        )

        self.conversation = ConversationChain(
            llm=self.llm,
            memory=ConversationBufferMemory(),
        )

    def chatbot(self, input):
        res = self.conversation.predict(input=input)
        return res


class BhashiniWrapper:
    def __init__(self) -> None:
        self.headers = Credentials().get_bhashini_headers()

    def convert_response_audio(self, text, audioln, filename):
        api_endpoint = "https://tts.bhashini.ai/v1/synthesize"

        payload = {"text": text, "languageId": audioln, "voiceId": 1}
        response = requests.post(api_endpoint, json=payload, headers=self.headers)

        if response.status_code == 200:
            audio = AudioSegment.from_file(io.BytesIO(response.content))
            audio.export(
                filename,
                format="wav",
            )

        else:
            print("Hello", response.encoding)
            print(f"Error: {response.status_code}, {response.text}")

    def convert_response(
        self,
        text,
        outputlan,
        lan_code,
        filename: str = None,
    ):
        api_endpoint = "https://tts.bhashini.ai/v1/translate"

        payload = {
            "inputText": text,
            "inputLanguage": "English",
            "outputLanguage": outputlan,
        }

        response = requests.post(api_endpoint, headers=self.headers, json=payload)

        if response.status_code == 200:
            response_content = response.content
            response_text = response_content.decode("utf-8")
            if filename:
                self.convert_response_audio(response_text, lan_code, filename)
            return response_text
        else:
            print(f"Error: {response.status_code}, {response.text}")


# if __name__ == "__main__":
#     string_store = ""
#     while True:
#         print("########################################\n")
#         pt = input("ASK: ")
#         if pt.lower() == "end":
#             convert_response(string_store, "Kannada")
#             break
#         response = chatbot(pt)
#         string_store += response
#         print("\n----------------------------------------\n")
#         print("ChatGPT says: \n")
#         print(response, "\n")
