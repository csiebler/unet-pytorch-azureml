from azureml.contrib.services.aml_request import AMLRequest, rawhttp
from azureml.contrib.services.aml_response import AMLResponse
from azureml.core.model import Model

import torch
from unet import UNet
from collections import OrderedDict

import numpy as np
from PIL import Image
from torchvision import transforms
import torch as t
from torchvision.transforms import ToPILImage

import io


def init():
    global unet
    global device
    model_path = Model.get_model_path(model_name='brain-segmentation-pytorch')
    #model_path = Model.get_model_path(model_name='unet.pt')

    print("Loading model from", model_path)
    
    device = torch.device("cpu" if not torch.cuda.is_available() else "cuda:0")
    print("Using device", device)
    state_dict = torch.load(model_path, map_location=device)
    
    unet = UNet(in_channels=3, out_channels=1)
    
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k[7:]
        new_state_dict[name] = v

    unet.load_state_dict(new_state_dict)
    if torch.cuda.is_available():
        unet = unet.to(device)

@rawhttp
def run(request):
    if request.method == 'POST':
        reqBody = request.get_data(False)
        resp = score(reqBody)
        return AMLResponse(resp, 200)
    if request.method == 'GET':
        respBody = str.encode("GET is not supported")
        return AMLResponse(respBody, 405)
    return AMLResponse("bad request", 500)


def score(data):
    input_image = Image.open(io.BytesIO(data))

    m, s = np.mean(input_image, axis=(0, 1)), np.std(input_image, axis=(0, 1))
    preprocess = transforms.Compose([
        transforms.ToTensor(),
    ])
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)

    input_batch = input_batch.to(device)

    with torch.no_grad():
        output = unet(input_batch)

    result = torch.round(output[0]).cpu()
    
    print(result)

    to_img = ToPILImage()
    mask = to_img(result)

    imgByteArr = io.BytesIO()
    mask.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()

    return imgByteArr

def test():
    init()
    with open("TCGA_CS_4944.png", 'rb') as f:
        content = f.read()
        result = score(content)
        with open("TCGA_CS_4944_maskresult.png", "wb") as aaff:
            aaff.write(result)

