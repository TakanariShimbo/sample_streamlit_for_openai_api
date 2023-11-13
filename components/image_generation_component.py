from typing import Union

import cv2
import numpy as np
from pydantic import BaseModel, ValidationError, Field
import requests
import streamlit as st

from enums.image_generation_enum import ImageGenerationModelEnum, ImageGenerationSizeEnum, ImageGenerationQualityEnum
from session_states.image_generation_s_states import ImageGenerationSStates
from handlers.enum_handler import EnumHandler
from handlers.image_generation_handler import ImageGenerationHandler
from components.base import SubComponentResult


class FormsSchema(BaseModel):
    model: str
    size: str
    quality: str
    prompt: str = Field(min_length=1)

    @property
    def model_type(self) -> ImageGenerationModelEnum:
        return EnumHandler.value_to_enum_member(enum=ImageGenerationModelEnum, value=self.model)

    @property
    def size_type(self) -> ImageGenerationSizeEnum:
        return EnumHandler.value_to_enum_member(enum=ImageGenerationSizeEnum, value=self.size)

    @property
    def quality_type(self) -> ImageGenerationQualityEnum:
        return EnumHandler.value_to_enum_member(enum=ImageGenerationQualityEnum, value=self.quality)


class OnSubmitHandler:
    @staticmethod
    def lock_submit_button() -> None:
        ImageGenerationSStates.set_submit_button_state(is_locked=True)

    @staticmethod
    def unlock_submit_button() -> None:
        ImageGenerationSStates.set_submit_button_state()

    @staticmethod
    def generate_image(form_values_schema: FormsSchema) -> str:
        image_url = ImageGenerationHandler.get_image_url(
            prompt=form_values_schema.prompt,
            model_type=form_values_schema.model_type,
            size_type=form_values_schema.size_type,
            quality_type=form_values_schema.quality_type,
        )
        return image_url

    @staticmethod
    def download_image(image_url: str) -> np.ndarray:
        response = requests.get(url=image_url)
        response.raise_for_status()
        image_bytes = bytearray(response.content)
        image_bgr = cv2.imdecode(buf=np.asarray(image_bytes, dtype=np.uint8), flags=cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(src=image_bgr, code=cv2.COLOR_BGR2RGB)
        return image_rgb

    @staticmethod
    def update_s_states(
        form_values_schema: FormsSchema,
        generated_image: Union[np.ndarray, str],
    ) -> None:
        ImageGenerationSStates.set_model_type(model_type=form_values_schema.model_type)
        ImageGenerationSStates.set_size_type(size_type=form_values_schema.size_type)
        ImageGenerationSStates.set_quality_type(quality_type=form_values_schema.quality_type)
        ImageGenerationSStates.set_inputed_prompt(inputed_prompt=form_values_schema.prompt)
        ImageGenerationSStates.set_generated_image(generated_image=generated_image)

    @staticmethod
    def set_error_message(error_message: str = "Please fill out the form completely.") -> None:
        ImageGenerationSStates.set_error_message(error_message=error_message)

    @staticmethod
    def reset_error_message() -> None:
        ImageGenerationSStates.set_error_message()


class ImageGenerationComponent:
    @classmethod
    def display_component(cls) -> None:
        res = cls.__sub_component()
        if res.call_return:
            st.rerun()

    @staticmethod
    def __sub_component() -> SubComponentResult:
        forms_dict = {}
        form = st.form(key="Image Generation Form")
        with form:
            setting_col = st.columns(3)

            # --- DALL-E Model select ---
            forms_dict["model"] = setting_col[0].selectbox(
                label="Model",
                options=EnumHandler.get_enum_member_values(enum=ImageGenerationModelEnum),
                index=EnumHandler.enum_member_to_index(member=ImageGenerationSStates.get_model_type()),
                placeholder="Select model...",
            )

            # --- Size select ---
            forms_dict["size"] = setting_col[1].selectbox(
                label="Size",
                options=EnumHandler.get_enum_member_values(enum=ImageGenerationSizeEnum),
                index=EnumHandler.enum_member_to_index(member=ImageGenerationSStates.get_size_type()),
                placeholder="Select size...",
            )

            # --- Quality select ---
            forms_dict["quality"] = setting_col[2].selectbox(
                label="Quality",
                options=EnumHandler.get_enum_member_values(enum=ImageGenerationQualityEnum),
                index=EnumHandler.enum_member_to_index(member=ImageGenerationSStates.get_quality_type()),
                placeholder="Quality size...",
            )

            # --- Text area ---
            forms_dict["prompt"] = st.text_area(
                label="Prompt",
                disabled=ImageGenerationSStates.get_submit_button_state(),
                value=ImageGenerationSStates.get_inputed_prompt(),
                placeholder="Please enter a description of the image to be generated",
            )

            # --- Submit button ---
            is_submited = st.form_submit_button(
                label="Sumbit",
                disabled=ImageGenerationSStates.get_submit_button_state(),
                on_click=OnSubmitHandler.lock_submit_button,
                type="primary",
            )

        if is_submited:
            try:
                form_values_schema = FormsSchema(**forms_dict)
            except ValidationError:
                OnSubmitHandler.set_error_message()
                OnSubmitHandler.unlock_submit_button()
                return SubComponentResult(call_rerun=True)

            with st.status("Generating..."):
                st.write("Querying...")
                generated_image_url = OnSubmitHandler.generate_image(form_values_schema=form_values_schema)
                st.write(f"[Downloading...]({generated_image_url})")
                generated_image_rgb = OnSubmitHandler.download_image(image_url=generated_image_url)

            OnSubmitHandler.update_s_states(
                form_values_schema=form_values_schema,
                generated_image=generated_image_rgb,
            )

            OnSubmitHandler.reset_error_message()
            OnSubmitHandler.unlock_submit_button()
            return SubComponentResult(call_rerun=True)

        try:
            form_values_schema = FormsSchema(**forms_dict)
        except ValidationError:
            error_message = ImageGenerationSStates.get_error_message()
            if error_message:
                with form:
                    st.warning(error_message)

        st.image(
            image=ImageGenerationSStates.get_generated_image(),
            caption=ImageGenerationSStates.get_inputed_prompt(),
            use_column_width=True,
        )
        return SubComponentResult()
