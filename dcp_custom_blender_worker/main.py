import os
import sys
import tempfile
import bpy
from typing import Annotated
from fastapi.routing import APIRoute
from fastapi import FastAPI, Request
import base64
import multiprocessing


def generate_app(cores):
    app = FastAPI()
    cores = max(1, cores)
    cores = min(cores, multiprocessing.cpu_count())

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
            for scene in bpy.data.scenes:
                scene.render.engine = "CYCLES"
                scene.render.threads_mode = "FIXED"
                scene.render.threads = cores

            for compute_device_type in ('CUDA', 'OPTIX', 'HIP', 'ONEAPI', 'NONE'):
                try:
                    bpy.context.preferences.addons[
                        "cycles"
                    ].preferences.compute_device_type = compute_device_type
                    print("Found device: ", compute_device_type)
                    break
                except Exception:
                    print(
                        f"Could not set compute_device_type to {compute_device_type}")
                    pass

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
    return app


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="BlenderRenderEngine")
    parser.add_argument("-p", "--port", default=8001, type=int)
    parser.add_argument(
        "-c", "--cores", default=(multiprocessing.cpu_count()//2)+1, type=int)
    args = parser.parse_args()

    app = generate_app(args.cores)
    uvicorn.run(app, host="0.0.0.0", port=int(args.port))
