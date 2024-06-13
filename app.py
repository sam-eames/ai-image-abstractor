import streamlit as st
from io import BytesIO
from PIL import Image
import spacy
import spacy_wordnet
from spacy_wordnet.wordnet_annotator import WordnetAnnotator



from image_generation import (authenticate_genai_client, authenticate_vision_client,
                              prompt_to_image, image_loop, load_image_from_url, DEFAULT_SIZE)


# util functions
def display_starter_image(image_bytes):
    st.header('Starting Image:')
    
    image_file = BytesIO(image_bytes)
    image = Image.open(image_file).resize(DEFAULT_SIZE)
    left_co, cent_co, right_co = st.columns(3)
    with cent_co:
        st.image(image)

# Page setup
st.title('Image Abstraction Looper')

with st.sidebar:
    st.subheader('Configuration')
    num_loops = st.number_input("Select number of loops", value = 1,
                                min_value = 1, max_value = 5)
    beginning_option = st.radio('Input selection', ['Text', 'Image'])
    caption_mode = st.radio('Dense Captions?', ['Regular', 'Dense'])
    prompt_randomisation = st.checkbox('Randomise prompts?', True)
    
    nlp = None
    if prompt_randomisation:
        num_to_replace = st.number_input("Select number of words to replace",
                                        value = 1, min_value = 1, max_value = 50)
        
        # set up spacy pipeline
        nlp = spacy.load('en_core_web_md')
        nlp.add_pipe("spacy_wordnet", after='tagger')


# Authenticate/setup
genai_client = authenticate_genai_client()
vision_client = authenticate_vision_client()

image_bytes = None
start_loop = None

# Set up initial image
st.header('Initial Input:')

if beginning_option == 'Image':
    initial_image = st.file_uploader('Provide an initial image')

    if initial_image is not None:
        image_bytes = initial_image.getvalue()
        display_starter_image(image_bytes)        
        
elif beginning_option == 'Text':
    initial_prompt = st.text_input('Provide an initial prompt')

# if inputs valid, display start button
if (beginning_option == 'Image'
    or (beginning_option == 'Text' and initial_prompt != '')):
    start_loop = st.button('Start Running')

if start_loop:
    # for prompt inputs, generate first image
    if beginning_option == 'Text':
        image_url = prompt_to_image(genai_client, initial_prompt)
        image_bytes = load_image_from_url(image_url)
        display_starter_image(image_bytes)

    st.header('Results')
    
    for i in range(num_loops):

        # overwrite current_caption, use image_bytes as input for next loop
        current_caption, image_prompt, image_bytes = image_loop(vision_client, genai_client,
                                                                image_bytes, caption_mode, nlp,
                                                                num_to_replace)
        
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
                st.caption('Caption')
                st.write(current_caption)
                st.caption('Prompt')
                st.write(image_prompt)
