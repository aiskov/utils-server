import os
import uuid
import BaseHTTPServer
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from urllib import urlopen
from urlparse import urlparse
from urlparse import parse_qs
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from cStringIO import StringIO

"""
apt-get install python-pip
apt-get build-dep python-imaging
apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev
pip install Pillow
"""

# Config
host = ''
port = 80
protocol = 'HTTP/1.0'
font_location = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'


# Util functions
def open_remote_image(url):
    url = url if url.startswith("http") else "http://%s" % url

    source = StringIO(urlopen(url).read())
    return Image.open(source)


def parse_query_params(query_string):
    return {k:v[0] for k, v in parse_qs(query_string).iteritems()}


def calculate_font_size(image_size, text, proportion=3):
    size = 1

    while True:
        selected = ImageFont.truetype(font_location, size)
        width, height = selected.getsize(text)

        if width * proportion > image_size[0] or height * proportion > image_size[1]:
            return selected

        size += 1


def calculate_center(font_size, image_size):
    return (int(image_size[0] / 2 - font_size[0] / 2), int(image_size[1] / 2 - font_size[1] / 2))


# Handler
class MainHandler(SimpleHTTPRequestHandler):
    def send_resource(self, name):
        self.path = name
        SimpleHTTPRequestHandler.do_GET(self)

    def do_GET(self):
        query = urlparse(self.path)
        params = parse_query_params(query.query)

        if query.path == "/pdf" and params.get('url'):
            name = 'tmp/%s.pdf' % str(uuid.uuid4())
            os.system('wkhtmltopdf %s %s' % (params.get('url'), name))

            self.send_resource(name)
            return
        elif query.path == '/img' and params.get('url'):
            name = 'tmp/%s.png' % str(uuid.uuid4())
            os.system('wkhtmltoimage %s %s' % (params.get('url'), name))

            self.send_resource(name)
            return
        elif query.path == '/resize' and params.get('url'):
            x = params.get('x')
            y = params.get('y')

            size = x if x else 450, y if y else 450

            name = 'tmp/%s.png' % str(uuid.uuid4())

            target = open_remote_image(params.get('url'))
            target.thumbnail(size, Image.ANTIALIAS)
            target.save(name, "PNG")

            self.send_resource(name)
            return
        elif query.path == '/watermark' and params.get('url') and params.get('text'):
            name = 'tmp/%s.png' % str(uuid.uuid4())
            proportion = params.get('proportion', 1.5)
            text = params.get('text')

            target = open_remote_image(params.get('url'))
            watermark = Image.new("RGBA", target.size)
            selected_font = calculate_font_size(target.size, text, proportion)

            waterdraw = ImageDraw.ImageDraw(watermark, "RGBA")
            waterdraw.setfont(selected_font)
            waterdraw.text(calculate_center(selected_font.getsize(text), target.size), text)

            watermark.putalpha(watermark.convert("L").point(lambda x: min(x, 100)))
            target.paste(watermark, None, watermark)
            target.save(name, "PNG")

            self.send_resource(name)
            return

        self.send_response(404)

MainHandler.protocol_version = protocol


# Server
class Server(ThreadingMixIn, HTTPServer):
    pass


# Execution
if __name__ == '__main__':
    try:
        server = Server((host, port), MainHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down server')
        server.socket.close()
