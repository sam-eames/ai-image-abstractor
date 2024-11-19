import json
import configparser
import requests
import io
import os
import uuid
from PIL import Image
from openai import AzureOpenAI
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from nlp_utils import replace_random_tokens

DEFAULT_SIZE = (300, 300)

Config = configparser.ConfigParser()
Config.read("config.ini")


def authenticate_genai_client():
    genai_client = AzureOpenAI(
        api_version="2024-02-01",
        azure_endpoint=Config.get('Genai Details', 'Endpoint'),
        api_key=Config.get('Genai Details', 'Key'),
    )
    return genai_client

def authenticate_vision_client():
    vision_client = ImageAnalysisClient(
        endpoint=Config.get('Vision Details', 'Endpoint'),
        credential=AzureKeyCredential(Config.get('Vision Details', 'Key'))
    )

    return vision_client

def prompt_to_image(genai_client, image_prompt):
    '''Query Azure Openai studio with provided <image_prompt> to generate image'''
    result = genai_client.images.generate(
        model = Config.get('Genai Details', 'Dalle Deployment'),
        prompt = image_prompt,
        n = 1
    )

    image_url = json.loads(result.model_dump_json())['data'][0]['url']

    return image_url

def load_image_from_url(image_url):
    '''Return image as pillow object from image'''
    img_data = requests.get(image_url).content

    # While testing locally, save image (comment out when deployed)
    # file_bytes = io.BytesIO(img_data)
    # image = Image.open(file_bytes)

    # output_folder = os.path.join(os.getcwd(), 'output_images')
    # if not os.path.exists(output_folder):
    #     os.mkdir(output_folder)
    # image.save(os.path.join(output_folder, f'image_{str(uuid.uuid4())}.jpg'))

    return img_data

def image_to_prompt(vision_client, large_image_bytes):
    '''
    Query Azure Openai studio with provided <image_url> to generate caption
    
    Return:
    caption - single sentence caption for entire image
    dense_captions - segmented captions across different areas of the image
    '''
    
    # reduce image size by converting to PIL (bytes > PIL + resize > bytes)
    image_bytes = io.BytesIO()
    image = Image.open(io.BytesIO(large_image_bytes))
    image.resize(DEFAULT_SIZE).save(image_bytes, "JPEG")
    image_bytes.seek(0)

    result = vision_client.analyze(
        image_data = image_bytes,
        visual_features = [VisualFeatures.CAPTION, VisualFeatures.DENSE_CAPTIONS]
    )

    if result.caption is None or result.dense_captions is None:
        raise ValueError(f'Caption generation failed, output values missing')
    
    caption = result.caption.text


    dense_captions = ' with a '.join(
        [caption["text"] for caption in result.dense_captions['values']]
        )
    # dense_captions = '\n'.join(
    #     [f'text: {caption["text"]}, bounding box: {caption["boundingBox"]}'
    #      for caption in result.dense_captions['values']]
    #     )

    return caption, dense_captions

# TODO: image logic loop
def image_loop(vision_client, genai_client, image_bytes,
               caption_mode, nlp, num_to_replace):
    '''
    Run through one loop of image > caption > image
    
    Return:
    caption - intermediate caption
    output_image_bytes - bytes of output image
    '''

    caption, dense_captions = image_to_prompt(vision_client, image_bytes)

    print(caption, dense_captions)

    image_prompt = dense_captions if caption_mode == 'Dense' else caption
    
    if nlp is not None:
        image_prompt = replace_random_tokens(nlp, image_prompt, num_to_replace)

    image_url = prompt_to_image(genai_client, image_prompt)
    output_image_bytes = load_image_from_url(image_url)

    # io.BytesIO(img_data)

    return caption, image_prompt, output_image_bytes


# # TODO: Define prompt to randomise word
# def randomise_prompt(prompt, num_words=1):
#     pass
