from django.http import HttpResponse
from PIL import Image
import os
import base64
import requests

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import openai
from django.shortcuts import redirect
from utils.chirp import CHIRP
from ai.models import ChatApiRequest

stability_api_key = "sk-heMfVLMb0aM0y6VVHDOZJI2nzFppBcAEEkIoHSgC3rAqXReu"
openai.api_key = os.environ.get("OPEN_AI_KEY", "")


# Supported image sizes for cropping
SUPPORTED_SIZES = [(1024, 1024), (1152, 896), (1216, 832), (1344, 768),
                   (1536, 640), (640, 1536), (768, 1344), (832, 1216),
                   (896, 1152)]


def find_best_crop(image_size):
    """
    Finds the best crop size from the supported sizes list for the given image size.

    Args:
        image_size (tuple): The size (width, height) of the input image.

    Returns:
        tuple: The best crop size (width, height).
    """
    best_crop = None
    best_diff = float('inf')

    for size in SUPPORTED_SIZES:
        diff = abs(image_size[0] / image_size[1] - size[0] / size[1])
        if diff < best_diff:
            best_diff = diff
            best_crop = size

    return best_crop


def crop_image(image_path):
    """
    Crops and resizes the input image to the best supported size.

    Args:
        image_path (str): The path to the input image file.
    """
    image = Image.open(image_path)
    # Convert the image to RGB mode
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    if image.mode == 'P':
        image = image.convert('RGB')

    image_size = image.size
    target_size = find_best_crop(image_size)

    target_ratio = target_size[0] / target_size[1]
    current_ratio = image_size[0] / image_size[1]

    if current_ratio > target_ratio:
        new_width = int(image_size[1] * target_ratio)
        image = image.crop(
            ((image_size[0] - new_width) // 2, 0, (image_size[0] + new_width) // 2, image_size[1]))
    else:
        new_height = int(image_size[0] / target_ratio)
        image = image.crop(
            (0, (image_size[1] - new_height) // 2, image_size[0], (image_size[1] + new_height) // 2))

    print(
        f"\nCurrent size: {image_size}\nClosest supported size: {target_size}\n")
    image = image.resize(target_size, Image.LANCZOS)
    image.save(image_path)


def image_to_image_stability(image_path, prompt):
    """
    Generates a new image based on the input image and text prompt using the Stability API.

    Args:
        image_path (str): The path to the input image file.
        prompt (str): The text prompt for generating the new image.

    Returns:
        list: List of generated image paths.
    """
    data = {
        "init_image_mode": "IMAGE_STRENGTH",
        "image_strength": 0.35,
        "samples": 1,
        "steps": 50,
        "seed": 0,
        "cfg_scale": 7,
        "style_preset": "enhance",
        "text_prompts[0][text]": prompt,
        "text_prompts[0][weight]": 1
    }

    if stability_api_key is None:
        raise Exception("Missing Stability API key.")

    # Call resize function
    crop_image(image_path)

    # Call the API to generate image based on the downloaded image
    response = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {stability_api_key}"
        },
        files={
            "init_image": open(image_path, "rb")
        },
        data=data
    )

    if response.status_code != 200:
        print("Failed to generate the image.")
        return

    data = response.json()

    image_paths = []
    for i, image in enumerate(data["artifacts"]):
        os.makedirs('/proj/rethinkdb-PG0/generated_images', exist_ok=True)
        # XXX lets save this in model file with inputs we used to create image
        image_path = f"/proj/rethinkdb-PG0/generated_images/{image['seed']}.png"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image["base64"]))
        image_paths.append(image['seed'])

    return image_paths

@api_view(["POST"])
def generate_image(request):
    print("HERE IS GENERATE IMAGE")
    print(request.FILES['video'])
    import uuid
    # XXX uploaded file might not be jpg
    uploaded_file = ("/tmp/%s-%s.jpg"
                     % (str(uuid.uuid4()), request.FILES['video']))
    with open(uploaded_file, "wb") as f:
        f.write(request.FILES['video'].read())

    # lets convert image to jpg
    #
    # os.system("convert %s %s" % (uploaded_file, uploade_file.split(".")[0] + ".jpg"))

    # Example usage:
    res = image_to_image_stability(
        uploaded_file,
        "convert this to a full futuristic lavish home")

    return redirect("/ai/get-image/%s/" % res[0])


@api_view(["POST"])
def input_chat(request):

    # Check if we have already seen this input_content
    car = ChatApiRequest.objects.filter(
        input_content=request.data.get("input_content")
    ).first()

    if car:
        car.asked_amount += 1
        car.save()
        return Response(car.response_content)

    car = ChatApiRequest()
    car.input_content = request.data.get("input_content")

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "system",
        "content": ""
        },
        {
        "role": "user",
        "content": request.data.get("input_content")
        }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    print(response)

    car.response_content = response['choices'][0]['message']['content']
    car.model = response['model']
    car.prompt_tokens = response['usage']['prompt_tokens']
    car.completion_tokens = response['usage']['completion_tokens']
    car.total_tokens = response['usage']['total_tokens']
    car.save()

    return Response(response['choices'][0]['message']['content'])



@api_view(["GET"])
def get_requests(request):
    return Response(ChatApiRequest.objects.filter().values())


@api_view(["GET"])
def get_image(request, seed):
    try:
        with open(
            "/proj/rethinkdb-PG0/generated_images/%s.png"
            % (seed), "rb"
        ) as f:
            return HttpResponse(f.read(), content_type="image/png")
    except IOError as e:
        CHIRP.info(e)
        return Response("no image")
