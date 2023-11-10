from typing import Any, Dict, List, Callable

from openai import OpenAI

from enums.chatgpt_enum import ChatGptModelEnum, ChatSenderEnum
from enums.env_enum import EnvEnum


class ChatGptHandler:
    client = OpenAI(api_key=EnvEnum.DEFAULT_OPENAI_APIKEY.value)

    @classmethod
    def query_streamly(
        cls,
        prompt: str,
        chat_history: List[Dict[str, str]] = [],
        model_type: ChatGptModelEnum = ChatGptModelEnum.GPT_3_5_TURBO,
    ) -> Any:
        copyed_chat_history = chat_history.copy()
        copyed_chat_history.append({"role": ChatSenderEnum.USER.value, "content": prompt})

        stream_response = cls.client.chat.completions.create(
            model=model_type.value,
            messages=copyed_chat_history,
            stream=True,
        )
        return stream_response

    @staticmethod
    def display_answer_streamly(
        stream_response: Any,
        display_func: Callable[[str], None],
    ) -> str:
        answer = ""
        for chunk in stream_response:
            answer_peace = chunk.choices[0].delta.content or ""
            answer += answer_peace
            display_func(answer)
        return answer

    @classmethod
    def query_and_display_answer_streamly(
        cls,
        prompt: str,
        display_func: Callable[[str], None],
        chat_history: List[Dict[str, str]] = [],
        model_type: ChatGptModelEnum = ChatGptModelEnum.GPT_3_5_TURBO,
    ) -> str:
        stream_response = cls.query_streamly(prompt=prompt, chat_history=chat_history, model_type=model_type)
        answer = cls.display_answer_streamly(stream_response=stream_response, display_func=display_func)
        return answer
