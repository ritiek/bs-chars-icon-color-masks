from PIL import Image
import cv2
import numpy as np
import os
import ast
import asyncio
from aiohttp import web

routes = web.RouteTableDef()


async def parse_tuple(string):
    try:
        s = ast.literal_eval(str(string))
        if type(s) == tuple:
            return s
        return
    except:
        return


async def _get_texture_path(texture):
    texture = os.path.join(TEXTURE_DIRECTORY, texture) + ".dds"
    return texture


class ApplyColorMask:
    def __init__(self, icon=None, mask=None, main_color=(0,0,0), highlight_color=(0,0,0)):
        self.set_icon(icon)
        self.set_mask(mask)
        self.set_main_color(main_color)
        self.set_highlight_color(highlight_color)

    def set_icon(self, icon):
        self._icon = icon

    def set_mask(self, mask):
        self._mask = mask

    def set_main_color(self, color):
        self._main_color = color

    def set_highlight_color(self, color):
        self._highlight_color = color

    def _create_blank(self, width=256, height=256, color=(0,0,0)):
        color = tuple([x * 255.0 for x in color])
        image = np.zeros((height, width, 4), np.uint8)
        rgb = list(reversed(color))
        rgba = tuple(rgb + [255.0])
        image[:] = rgba
        return image

    def _apply_color(self, base_icon, mask, color):
        height, width, _ = base_icon.shape
        color = self._create_blank(width, height, color=color)
        part = cv2.bitwise_and(color, color, mask=mask)
        r,g,b,_ = cv2.split(part)
        part = cv2.merge((r,g,b,mask))

        base_icon = base_icon.astype(float)
        part_color = base_icon
        part = part.astype(float)
        alpha = base_icon/255.0

        part_color = cv2.multiply(alpha, part)
        part = cv2.multiply(1.0 - alpha, part_color)
        part_color = cv2.add(part_color, part)

        alpha = cv2.merge((mask, mask, mask, mask))/255.0
        part_color = cv2.multiply(alpha, part_color)
        base_icon = cv2.multiply(1.0 - alpha, base_icon)

        base_icon = cv2.add(part_color, base_icon)
        return base_icon

    async def _read(self, path):
        image = Image.open(path)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
        return image

    async def apply_transformation(self):
        base_icon, mask = await asyncio.gather(self._read(self._icon), self._read(self._mask))
        mask = cv2.resize(mask, base_icon.shape[1::-1])

        mask_red_channel = mask[:,:,2]
        base_icon = self._apply_color(base_icon, mask_red_channel, self._main_color)

        mask_green_channel = mask[:,:,1]
        base_icon = self._apply_color(base_icon, mask_green_channel, self._highlight_color)

        # Remove alpha channel
        return base_icon[:,:,:3]



@routes.get("/")
async def do_GET(request):
    query_components = request.rel_url.query
    try:
        icon = query_components["icon"]
        mask = query_components["mask"]
        main_color, highlight_color = parse_tuple(query_components["main"]), parse_tuple(query_components["highlight"])
        main_color, highlight_color = await asyncio.gather(main_color, highlight_color)
    except KeyError:
        return
    icon, mask = await asyncio.gather(_get_texture_path(icon), _get_texture_path(mask))
    main_color, highlight_color = tuple(map(float, main_color)), tuple(map(float, highlight_color))
    filename = "{} with {} ({}, {}).png".format(icon, mask, main_color, highlight_color)
    spaz = ApplyColorMask(icon, mask, main_color, highlight_color)
    image = await spaz.apply_transformation()
    _, image = cv2.imencode(".png", image)
    return web.Response(body=image.tobytes(), content_type="image/png")


if __name__ == "__main__":
    import sys
    try:
        TEXTURE_DIRECTORY = sys.argv[1]
        PORT = int(sys.argv[2])
    except IndexError:
        print("Usage: python", sys.argv[0], "<path/to/bombsquad/textures/directory>", "<webserver-port>")
        sys.exit(1)
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host="0.0.0.0", port=PORT)
