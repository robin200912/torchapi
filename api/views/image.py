import io
import os

import PIL.Image
import sanic
import torchvision
from sanic import Blueprint
from sanic import Sanic

from api.algo.core.runner import ModelRunner
from api.utils import HandlingError

__all__ = ["image_bp"]

app = Sanic.get_app()

image_bp = Blueprint("image_bp", url_prefix="/info")

model_name = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "algo",
                          "data",
                          "horse2zebra_0.4.0.pth")
style_transfer_runner = ModelRunner(app, model_name)


@app.route('/image', methods=['PUT'], stream=True)
async def image(request):
    try:
        print(request.headers)
        content_length = int(request.headers.get('content-length', '0'))
        MAX_SIZE = 2 ** 22  # 10MB
        if content_length:
            if content_length > MAX_SIZE:
                raise HandlingError("Too large")
            data = bytearray(content_length)
        else:
            data = bytearray(MAX_SIZE)
        pos = 0
        while True:
            data_part = await request.stream.read()
            if data_part is None:
                break
            data[pos: len(data_part) + pos] = data_part
            pos += len(data_part)
            if pos > MAX_SIZE:
                raise HandlingError("Too large")

        im = PIL.Image.open(io.BytesIO(data))
        im = torchvision.transforms.functional.resize(im, (228, 228))
        im = torchvision.transforms.functional.to_tensor(im)
        im = im[:3]
        if im.dim() != 3 or im.size(0) < 3 or im.size(0) > 4:
            raise HandlingError("need rgb image")
        out_im = await style_transfer_runner.process_input(im)

        out_im = torchvision.transforms.functional.to_pil_image(out_im)
        imgByteArr = io.BytesIO()
        out_im.save(imgByteArr, format='JPEG')
        return sanic.response.raw(imgByteArr.getvalue(), status=200,
                                  content_type='image/jpeg')
    except HandlingError as e:
        return sanic.response.text(e.handling_msg, status=e.handling_code)


app.add_task(style_transfer_runner.model_runner())
