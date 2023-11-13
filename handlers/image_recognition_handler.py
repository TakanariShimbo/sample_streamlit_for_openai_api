from typing import Any, Callable

from openai import OpenAI

from enums.chatgpt_enum import ChatSenderEnum
from enums.env_enum import EnvEnum


VISION_MODEL = "gpt-4-vision-preview"


class ImageRecognitionHandler:
    client = OpenAI(api_key=EnvEnum.DEFAULT_OPENAI_APIKEY.value)

    @classmethod
    def query(
        cls,
        image_b64: str,
        prompt: str = "この画像を200字程度で説明をしてください。",
    ) -> str:
        response = cls.client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                cls.__get_user_prompt_with_image(prompt=prompt, image_b64=image_b64),
            ],
            max_tokens=1000,
        )

        answer = response.choices[0].message.content
        return answer

    @classmethod
    def query_and_display_answer_streamly(
        cls,
        image_b64: str,
        prompt: str = "この画像を200字程度で説明をしてください。",
        display_func: Callable[[str], None] = print,
    ) -> str:
        stream_response = cls.client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                cls.__get_user_prompt_with_image(prompt=prompt, image_b64=image_b64),
            ],
            stream=True,
            max_tokens=1000,
        )

        answer = ""
        for chunk in stream_response:
            answer_peace = chunk.choices[0].delta.content or ""  # type: ignore
            answer += answer_peace
            display_func(answer)
        return answer

    @staticmethod
    def __get_user_prompt_with_image(prompt: str, image_b64: str) -> Any:
        return {
            "role": ChatSenderEnum.USER.value,
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                },
            ],
        }