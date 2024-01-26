import io
from base64 import b64encode

from django.shortcuts import render
from django.conf import settings
from .forms import ImageUploadForm

from torchvision import transforms
from PIL import Image
import torch


def index(request):
    return render(request, 'segmentation/index.html')


def components(request):
    return render(request, 'segmentation/components.html')


def ml_model(request):
    image_uri = None
    uploaded_image_uri = None

    if request.method == 'POST':
        # in case of POST: get the uploaded image from the form and process it
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():

            # Uploaded image
            uploaded_image = form.cleaned_data['image']
            uploaded_image_bytes = uploaded_image.file.read()
            # convert and pass the image as base64 string to avoid storing it to DB or filesystem
            encoded_img = b64encode(uploaded_image_bytes).decode('ascii')
            uploaded_image_uri = 'data:%s;base64,%s' % ('image/jpeg', encoded_img)

            # retrieve the uploaded image and convert it to bytes (for PyTorch)
            image = form.cleaned_data.get('image')
            image = Image.open(image)

            # get predicted label with previously implemented PyTorch function
            try:
                image_uri = get_prediction(image)

                # Transfer to bytes
                buf = io.BytesIO()
                image_uri.save(buf, format='JPEG')
                byte_im = buf.getvalue()
                encoded = b64encode(byte_im).decode('ascii')
                mime = "image/jpg"
                mime = mime + ";" if mime else ";"
                image_uri = "data:%sbase64,%s" % (mime, encoded)

            except RuntimeError as re:
                print(re)

    else:
        # in case of GET: simply show the empty form for uploading images
        form = ImageUploadForm()

    # pass the form, image URI, and predicted label to the template to be rendered
    context = {
        'form': form,
        'image_uri': image_uri,
        'input_image': uploaded_image_uri
    }

    return render(request, 'segmentation/ml_model.html', context)


model = torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_mobilenet_v3_large', pretrained=True)
model.eval()


def get_prediction(image_bytes):
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    input_tensor = preprocess(image_bytes)
    input_batch = input_tensor.unsqueeze(0)  # create a mini-batch as expected by the model

    with torch.no_grad():
        output = model(input_batch)['out'][0]

    output_predictions = output.argmax(0)

    palette = torch.tensor([2 ** 25 - 1, 2 ** 15 - 1, 2 ** 21 - 1])
    colors = torch.as_tensor([i for i in range(21)])[:, None] * palette
    colors = (colors % 255).numpy().astype("uint8")

    # plot the semantic segmentation predictions of 21 classes in each color
    r = Image.fromarray(output_predictions.byte().cpu().numpy()).resize(image_bytes.size)
    r.putpalette(colors)
    r.convert('RGB').save('res.jpeg')

    contents = r.convert('RGB')
    return contents
