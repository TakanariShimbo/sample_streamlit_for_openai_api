from typing import Optional

import numpy as np

from enums.s_state_enum import ImageRecognitionSStateEnum
from session_states.base_s_states import BaseSState


class SubmitSState(BaseSState[bool]):
    @staticmethod
    def get_name() -> str:
        return f"{ImageRecognitionSStateEnum.SUBMIT}"

    @staticmethod
    def get_default() -> bool:
        return False


class ErrorMessageSState(BaseSState[Optional[str]]):
    @staticmethod
    def get_name() -> str:
        return f"{ImageRecognitionSStateEnum.ERROR_MESSAGE}"

    @staticmethod
    def get_default() -> Optional[str]:
        return None


class PromptSState(BaseSState[Optional[str]]):
    @staticmethod
    def get_name() -> str:
        return f"{ImageRecognitionSStateEnum.PROMPT}"

    @staticmethod
    def get_default() -> Optional[str]:
        return None


class UploadedImageSState(BaseSState[Optional[np.ndarray]]):
    @staticmethod
    def get_name() -> str:
        return f"{ImageRecognitionSStateEnum.UPLOADED_IMAGE}"

    @staticmethod
    def get_default() -> Optional[np.ndarray]:
        return None
    

class AnswerSState(BaseSState[Optional[str]]):
    @staticmethod
    def get_name() -> str:
        return f"{ImageRecognitionSStateEnum.ANSWER}"

    @staticmethod
    def get_default() -> Optional[str]:
        return None