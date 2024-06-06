import streamlit as st
from io import BytesIO
from PIL import Image
from image_generation import (authenticate_genai_client, authenticate_vision_client,
                              prompt_to_image, load_image_from_url, image_loop)

DEFAULT_SIZE = (300, 300)

# Page setup
st.title('Image Abstraction Looper')

with st.sidebar:
    st.subheader('Configuration')
    beginning_option = st.radio('Input selection', ['Text', 'Image'])
    caption_mode = st.radio('Dense Captions?', ['Regular', 'Dense'])
    prompt_randomisation = st.checkbox('Randomise prompts?', True)

# Authenticate/setup
genai_client = authenticate_genai_client()
vision_client = authenticate_vision_client()

image_bytes = None

# Set up initial image
st.header('Initial Input:')

if beginning_option == 'Image':
    initial_image = st.file_uploader('Provide an initial image')

    if initial_image is not None:
        image_bytes = initial_image.getvalue()
        # image_bytes = BytesIO(bytes_data)
        

elif beginning_option == 'Text':
    initial_prompt = st.text_input('Provide an initial prompt')

    if initial_prompt != '':
        image_url = prompt_to_image(genai_client, initial_prompt)
        image_bytes = load_image_from_url(image_url)        

if image_bytes is not None:
    st.header('Starting Image:')
    
    image_file = BytesIO(image_bytes)
    image = Image.open(image_file).resize(DEFAULT_SIZE)
    left_co, cent_co, right_co = st.columns(3)
    with cent_co:
        st.image(image)

    st.header('Run Loops:')
    num_loops = st.number_input("Select number of loops", value = 1,
                                min_value = 1, max_value = 5)
    
    # Run loops
    start_loop = st.checkbox('Start Running')

    if start_loop:
        st.header('Results')
        
        for i in range(num_loops):

            # overwrite current_caption, use image_bytes as input for next loop
            current_caption, image_bytes = image_loop(vision_client, genai_client, image_bytes, caption_mode)
            
            image_file = BytesIO(image_bytes)
            current_image = Image.open(image_file).resize(DEFAULT_SIZE)

            # display results for each loop
            with st.spinner():
                st.subheader(f'Loop {i+1} Result')
                left_co, right_co = st.columns(2)
                
                with left_co:
                    st.caption('Image')
                    st.image(current_image)

                with right_co:
                    st.caption('Prompt')
                    st.write(current_caption)
