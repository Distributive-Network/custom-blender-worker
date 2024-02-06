import os
import sys
import tempfile
import bpy
from typing import Annotated
from fastapi.routing import APIRoute
from fastapi import FastAPI, Request
import base64

app = FastAPI()


@app.get('/status')
async def status():
    return {'status': 'ok'}


def _render(frame_number: int, blendFileBytes: bytes):

    with tempfile.TemporaryDirectory() as tmp:
        fileName = os.path.join(tmp, "input.blend")
        with open(fileName, 'wb') as f:
            f.write(blendFileBytes)
        bpy.ops.wm.open_mainfile(
            filepath=fileName, load_ui=False, use_scripts=False)
        print("Blend file loaded.")

        # Detect GPU
        bpy.context.preferences.addons['cycles'].preferences.get_devices()
        bpy.data.scenes[0].render.engine = "CYCLES"

        bpy.context.preferences.addons[
            "cycles"
        ].preferences.compute_device_type = "CUDA"

        scene = bpy.context.scene
        scene.cycles.device = "GPU"

        bpy.context.preferences.addons["cycles"].preferences.get_devices()
        # print(
        #    bpy.context.preferences.addons["cycles"].preferences.compute_device_type)

        for d in bpy.context.preferences.addons["cycles"].preferences.devices:
            d["use"] = 1  # Using all devices, include GPU and CPU
            print(d["name"], d["use"])

        # set output format to .png
        scene.render.image_settings.file_format = 'PNG'

        scene.frame_set(int(frame_number))
        print("Blend file set to frame: ", frame_number)

        scene.render.filepath = os.path.join(tmp, 'result.png')
        bpy.ops.render.render(write_still=True)

        with open(scene.render.filepath, 'rb') as f:
            retVal = f.read()
    return retVal


@app.post('/render/{frame_number}')
async def render(frame_number: int, request: Request):
    body = await request.body()
    retVal = _render(frame_number, body)
    retVal = base64.b64encode(retVal).decode('ascii')
    return retVal


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)
