from typing import Optional, Any

from pydantic import BaseModel, ValidationError
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from enums.speech_recognition_enum import ExtensionEnum, LanguageEnum
from handlers.enum_handler import EnumHandler
from handlers.speech_recognition_handler import SpeechRecognitionHandler
from session_states.speech_recognition_s_states import SubmitSState, ErrorMessageSState, LanguageTypeSState, StoredSpeechSState, StoredTranscriptSState
from components.sub_compornent_result import SubComponentResult


class FormSchema(BaseModel):
    language_type: LanguageEnum
    uploaded_speech_file: Any
    
    @classmethod
    def construct_using_form_dict(cls, language_type: LanguageEnum, uploaded_speech_file: UploadedFile):
         return cls(language_type=language_type, uploaded_speech_file=uploaded_speech_file)

    
class OnSubmitHandler:
    @staticmethod
    def lock_submit_button():
        SubmitSState.set(value=True)

    @staticmethod
    def unlock_submit_button():
        SubmitSState.reset()

    @staticmethod
    def set_error_message(error_message: str = "Please fill out the form completely.") -> None:
        ErrorMessageSState.set(value=error_message)

    @staticmethod
    def reset_error_message() -> None:
        ErrorMessageSState.reset()

    @staticmethod
    def display_audio(form_schema: FormSchema) -> None:
        st.audio(data=form_schema.uploaded_speech_file, format="audio/mp3")

    @staticmethod
    def recognize_speech(form_schema: FormSchema) -> Optional[str]:
        text = SpeechRecognitionHandler.recognize_speech(
            speech_file=form_schema.uploaded_speech_file,
            language_type=form_schema.language_type,
        )
        return text

    @staticmethod
    def update_s_states(form_schema: FormSchema, text: Optional[str]):
        LanguageTypeSState.set(value=form_schema.language_type)
        StoredSpeechSState.set(value=form_schema.uploaded_speech_file)
        if text:
            StoredTranscriptSState.set(value=text)


class SpeechRecognitionComponent:
    @classmethod
    def display_component(cls) -> None:
        res = cls.__sub_component()
        if res.call_return:
            st.rerun()

    @staticmethod
    def __sub_component() -> SubComponentResult:
        form_dict = {}
        form = st.form(key="SpeechRecognition_PromptForm", clear_on_submit=True)
        with form:
            st.markdown("#### Prompt Form")

            form_dict["language_type"] = st.selectbox(
                label="Language",
                options=EnumHandler.get_enum_members(enum=LanguageEnum),
                format_func=lambda x: x.name,
                index=EnumHandler.enum_member_to_index(member=LanguageTypeSState.get()),
                placeholder="Select model...",
                key="ChatGpt_LanguageSelectBox",
            )

            form_dict["uploaded_speech_file"] = st.file_uploader(
                label="Uploader", 
                type=EnumHandler.get_enum_member_values(enum=ExtensionEnum),
                key="SpeechRecognition_UploadedFile",
            )
            
            is_submited = st.form_submit_button(
                label="Submit",
                disabled=SubmitSState.get(),
                on_click=OnSubmitHandler.lock_submit_button,
                type="primary",
            )

        if is_submited:
            try:
                form_schema = FormSchema.construct_using_form_dict(**form_dict)
            except:
                OnSubmitHandler.set_error_message()
                OnSubmitHandler.unlock_submit_button()
                return SubComponentResult(call_rerun=True)
            
            st.markdown("#### Recognized result")
            OnSubmitHandler.display_audio(form_schema=form_schema)
            text = OnSubmitHandler.recognize_speech(form_schema=form_schema)

            OnSubmitHandler.update_s_states(form_schema=form_schema, text=text)
            OnSubmitHandler.reset_error_message()
            OnSubmitHandler.unlock_submit_button()
            return SubComponentResult(call_rerun=True)

        text = StoredTranscriptSState.get()
        if text:
            st.markdown("#### Recognized result")
            st.audio(data=StoredSpeechSState.get(), format="audio/mp3")
            st.write(text)

        return SubComponentResult()