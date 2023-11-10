from textwrap import dedent
import streamlit as st
from components.title_component import TitleComponent

from session_states.image_generation_s_states import ImageGenerationSStates
from enums.image_generation_enum import (
    ImageGenerationModelEnum,
    ImageGenerationSizeEnum,
    ImageGenerationQualityEnum,
)
from handlers.image_generation_handler import ImageGenerationHandler

from typing import Optional

"""
TITLE
"""
TitleComponent.set_page_configs(
    icon="🌅",
    title="Image Generation",
)


"""
CONTENTS
"""


def display_content() -> None:
    content = dedent(
        f"""
        This page performs image generation powered by DALL-E😊  
        Made by Shun🍓  
        """
    )
    st.markdown(content)


display_content()


def display_image():
    image_url = ImageGenerationSStates.get_image_url()
    if not image_url:
        return

    st.image(image_url, caption=inputed_user_prompt, use_column_width=True)
    st.link_button("Image URL", image_url)

    # display model setting


st.write("### Settings")
setting_col = st.columns(3)
# --- DALL-E Model select ---
selected_model_value = setting_col[0].selectbox(
    label="DALL-E Model",
    options=ImageGenerationModelEnum.to_value_list(),
    index=ImageGenerationModelEnum.from_enum_to_index(enum=ImageGenerationSStates.get_model_type()),
    placeholder="Select model...",
)
if selected_model_value:
    selected_model_type = ImageGenerationModelEnum.from_value_to_enum(value=selected_model_value)
    ImageGenerationSStates.set_model_type(model_type=selected_model_type)

# --- Size select ---
selected_size_value = setting_col[1].selectbox(
    label="Size",
    options=ImageGenerationSizeEnum.to_value_list(),
    index=ImageGenerationSizeEnum.from_enum_to_index(enum=ImageGenerationSStates.get_size_type()),
    placeholder="Select size...",
)
if selected_size_value:
    selected_size_type = ImageGenerationSizeEnum.from_value_to_enum(value=selected_size_value)
    ImageGenerationSStates.set_size_type(size_type=selected_size_type)

# --- Quality select ---
selected_quality_value = setting_col[2].selectbox(
    label="Quality",
    options=ImageGenerationQualityEnum.to_value_list(),
    index=ImageGenerationQualityEnum.from_enum_to_index(enum=ImageGenerationSStates.get_quality_type()),
    placeholder="Quality size...",
)
if selected_quality_value:
    selected_quality_type = ImageGenerationQualityEnum.from_value_to_enum(value=selected_quality_value)
    ImageGenerationSStates.set_quality_type(quality_type=selected_quality_type)

# --- Text area ---
inputed_user_prompt = st.text_area(
    label="User Prompt",
    value=ImageGenerationSStates.get_user_prompt(),
    placeholder="Please enter a description of the image to be generated",
)
if inputed_user_prompt:
    ImageGenerationSStates.set_user_prompt(user_prompt=inputed_user_prompt)

submit_button = st.button("Send", type="primary")


if submit_button:
    # if not (selected_model_value and selected_quality_value and selected_quality_value and inputed_user_prompt):
    #     st.error("Please select setting menu")
    # else:
    with st.spinner("Image generating..."):
        current_image_url = ImageGenerationSStates.get_image_url()
        image_url = ImageGenerationHandler.get_image_url(
            prompt=ImageGenerationSStates.get_user_prompt(),
            model_type=ImageGenerationSStates.get_model_type(),
            size_type=ImageGenerationSStates.get_size_type(),
            quality_type=ImageGenerationSStates.get_quality_type(),
        )
        if image_url:
            ImageGenerationSStates.set_image_url(image_url=image_url)
        st.success("Generation complete!")
        st.balloons()

display_image()
