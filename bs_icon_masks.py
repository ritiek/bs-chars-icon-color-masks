import cv2
import numpy as np
from PIL import Image

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

    def _read(self, path):
        image = Image.open(path)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
        return image

    def apply_transformation(self):
        base_icon = self._read(self._icon)
        mask = self._read(self._mask)
        mask = cv2.resize(mask, base_icon.shape[1::-1])

        mask_red_channel = mask[:,:,2]
        base_icon = self._apply_color(base_icon, mask_red_channel, self._main_color)

        mask_green_channel = mask[:,:,1]
        base_icon = self._apply_color(base_icon, mask_green_channel, self._highlight_color)

        # Remove alpha channel
        return base_icon[:,:,:3]


import ast

def parse_tuple(string):
    try:
        s = ast.literal_eval(str(string))
        if type(s) == tuple:
            return s
        return
    except:
        return


try:
    import BaseHTTPServer as Server
    import urlparse
except ImportError:
    import http.server as Server
    import urllib.parse as urlparse

import os

class ColorMaskServer(Server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

    def _get_texture_path(self, texture):
        texture = os.path.join(TEXTURE_DIRECTORY, texture) + ".dds"
        return texture

    def do_GET(self):
        query_components = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        try:
            icon = query_components["icon"][0]
            mask = query_components["mask"][0]
            main_color = tuple(map(float, parse_tuple(query_components["main"][0])))
            highlight_color = tuple(map(float, parse_tuple(query_components["highlight"][0])))
        except KeyError:
            return
        self.send_response(200)
        filename = "{} with {} ({}, {}).png".format(icon, mask, main_color, highlight_color)
        self.send_header("Content-Disposition", 'inline; filename="{}"'.format(filename))
        self.send_header("Content-Type", "image/png")
        self.end_headers()
        icon = self._get_texture_path(icon)
        mask = self._get_texture_path(mask)
        spaz = ApplyColorMask(icon, mask, main_color, highlight_color)
        image = spaz.apply_transformation()
        _, image = cv2.imencode(".png", image)
        self.wfile.write(image.tobytes())


if __name__ == "__main__":
    import sys
    try:
        TEXTURE_DIRECTORY = sys.argv[1]
        PORT = int(sys.argv[2])
    except IndexError:
        print("Usage: python", sys.argv[0], "<path/to/bombsquad/textures/directory>", "<webserver-port>")
        sys.exit(1)
    httpd = Server.HTTPServer(("0.0.0.0", PORT), ColorMaskServer)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

