from typing import Optional

from pydantic import BaseModel, ValidationError, Field
import streamlit as st

from enums.chatgpt_enum import AiModelEnum, SenderEnum
from handlers.enum_handler import EnumHandler
from handlers.chatgpt_handler import ChatGptHandler
from session_states.chat_gpt_s_states import SubmitSState, ErrorMessageSState, AiModelSState, ChatHistorySState
from components.sub_compornent_result import SubComponentResult


class FormSchema(BaseModel):
    ai_model_value: Optional[str]
    prompt: str = Field(min_length=1)

    @property
    def ai_model_type(self) -> AiModelEnum:
        return EnumHandler.value_to_enum_member(enum=AiModelEnum, value=self.ai_model_value)


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
    def display_prompt(prompt: str) -> None:
        with st.chat_message(name=SenderEnum.USER.value):
            st.write(prompt)

    @staticmethod
    def query_and_display_answer(form_schema: FormSchema) -> Optional[str]:
        if not form_schema.ai_model_type.value:
            return None

        with st.chat_message(name=form_schema.ai_model_type.value):
            answer_area = st.empty()
            answer = ChatGptHandler.query_and_display_answer_streamly(
                prompt=form_schema.prompt,
                display_func=answer_area.write,
                chat_history=ChatHistorySState.get_for_query(),
                model_type=form_schema.ai_model_type,
            )
        return answer

    @staticmethod
    def update_s_states(form_schema: FormSchema, answer: Optional[str]):
        AiModelSState.set(value=form_schema.ai_model_type)
        ChatHistorySState.add(sender_type=SenderEnum.USER, sender_name=SenderEnum.USER.name, content=form_schema.prompt)
        if form_schema.ai_model_type.value and answer:
            ChatHistorySState.add(sender_type=SenderEnum.ASSISTANT, sender_name=form_schema.ai_model_type.value, content=answer)


class ChatGptComponent:
    @classmethod
    def display_component(cls) -> None:
        res = cls.__sub_component()
        if res.call_return:
            st.rerun()

    @staticmethod
    def __sub_component() -> SubComponentResult:
        history_container = st.container()
        with history_container:
            st.markdown("#### Chat History")
            for chat in ChatHistorySState.get():
                with st.chat_message(name=chat["role_name"]):
                    st.write(chat["content"])

        form_dict = {}
        form = st.form(key="Chat GPT Form", clear_on_submit=True)
        with form:
            st.markdown("#### Prompt Form")
            
            form_dict["ai_model_value"] = st.selectbox(
                label="Model",
                options=EnumHandler.get_enum_member_values(enum=AiModelEnum),
                index=EnumHandler.enum_member_to_index(member=AiModelSState.get()),
                placeholder="Select model...",
                key="ChatGpt ModelSelectBox",
            )

            form_dict["prompt"] = st.text_area(
                label="Prompt",
                disabled=SubmitSState.get(),
                placeholder="Please input prompt...",
                key="ChatGpt PromptTextArea",
            )

            is_submited = st.form_submit_button(
                label="Sumbit",
                disabled=SubmitSState.get(),
                on_click=OnSubmitHandler.lock_submit_button,
                type="primary",
            )

        if is_submited:
            try:
                form_schema = FormSchema(**form_dict)
            except ValidationError:
                OnSubmitHandler.set_error_message()
                OnSubmitHandler.unlock_submit_button()
                return SubComponentResult(call_rerun=True)

            with history_container:
                OnSubmitHandler.display_prompt(prompt=form_schema.prompt)
                answer = OnSubmitHandler.query_and_display_answer(form_schema=form_schema)
            OnSubmitHandler.update_s_states(form_schema=form_schema, answer=answer)
            OnSubmitHandler.reset_error_message()
            OnSubmitHandler.unlock_submit_button()
            return SubComponentResult(call_rerun=True)

        return SubComponentResult()
