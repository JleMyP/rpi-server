#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from mimetypes import guess_type, init as init_mime
from urllib import unquote
from shutil import copyfileobj
import os, sys, cgi, time
import pygame

try:
  import RPi.GPIO as gpio
  gpio.setmode(gpio.BCM)
  l1, l2, lEn = 17, 18, 23
  r1, r2, rEn = 22, 27, 24
  #lpwm, rpwm = gpio.PWM(lEn, 500), gpio.PWM(rEn, 500)
  gpio.setup((l1, l2, lEn, r1, r2, rEn), gpio.OUT)
  #lpwm.start(100)
  #rpwm.start(100)
  #gpio.output(lEn, 1)
  #gpio.output(rEn, 1)
except:
  gpio = None



class ThreadHTTPServer(ThreadingMixIn, HTTPServer):
  def __init__(self, addr, handler):
    HTTPServer.__init__(self, addr, handler)



class Handler(BaseHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    BaseHTTPRequestHandler.__init__(self, *args, **kwargs)


  def do_GET(self):
    global move, n
    
    path, params = urlparse(self.path)
    print path, params
    
    if params:
      for cmd in ("forward", "back", "left", "right", "stop"):
        if gpio and cmd in params.keys():
          self.send_response(200)
          
          if move != cmd:
            eval(cmd + "()")
            move = cmd
          
          break
    else:
      if path != "/" and not os.path.exists(server_path+path):
        self.send_response(404)
        return

      path = server_path+path

      if os.path.isfile(path):
        self.send_response(200)
        self.send_header('content-type', guess_type(path)[0])
        self.send_header('content-length', os.path.getsize(path))
        self.end_headers()

        f = open(path, "rb")
        copyfileobj(f, self.wfile)
        f.close()
      else:
        files = [n for n in os.listdir(path) if os.path.isfile(path+n)]

        if "index.html" in files:
          path += "index.html"
          self.send_response(200)
          self.send_header('content-type', guess_type(path)[0])
          self.send_header('content-length', os.path.getsize(path))
          self.end_headers()

          f = open(path, "rb")
          copyfileobj(f, self.wfile)
          f.close()
          return

        dirs = [n for n in os.listdir(path) if not os.path.isfile(path + n)]
        files.sort(lambda a, b: cmp(a.lower(), b.lower()))
        dirs.sort(lambda a, b: cmp(a.lower(), b.lower()))
        otv = "<html><head><title>serva4ok</title></head><body>"

        for name in dirs: otv += '<a href="%s">%s</a><br>' % (name + "/", name + "/")
        for name in files: otv += '<a href="%s">%s</a><br>\n' % (name, name)

        otv += "</body></html>"
        otv = ur(otv)

        self.send_response(200)
        self.send_header('content-type', "text/html")
        self.send_header('content-length', len(otv))
        self.send_header('content-encoding', "utf-8")
        self.send_header('connection', 'close')
        self.end_headers()
        self.wfile.write(otv)



def urlparse(url):
  url = unquote(url).decode('utf-8')

  if '?' not in url: return url, {}

  path, query = url.split('?')
  params = {}

  for param in query.split('&'):
    k, v = param.split('=') if '=' in param else (param, '')
    params[k] = v

  return path, params


def forward():
  gpio.output(l1, 1)
  gpio.output(l2, 0)
  gpio.output(r1, 1)
  gpio.output(r2, 0)


def back():
  gpio.output(l1, 0)
  gpio.output(l2, 1)
  gpio.output(r1, 0)
  gpio.output(r2, 1)


def left():
  gpio.output(l1, 0)
  gpio.output(l2, 1)
  gpio.output(r1, 1)
  gpio.output(r2, 0)


def right():
  gpio.output(l1, 1)
  gpio.output(l2, 0)
  gpio.output(r1, 0)
  gpio.output(r2, 2)


def stop():
  gpio.output(l1, 0)
  gpio.output(l2, 0)
  gpio.output(r1, 0)
  gpio.output(r2, 0)



ru = lambda x: str(x).decode("utf-8")
ur = lambda x: str(x).encode("utf-8")


port = 80
move = "stop"
n = 0
server_path = sys.argv[1]
#server_path = os.path.dirname(sys.argv[0])+'/'

os.chdir(server_path)
init_mime()
pygame.font.init()
pygame.camera.init()
font = pygame.font.Font("freesansbold.ttf", 30)
serv = ThreadHTTPServer(('', port), Handler)

print "server start on %i port"%port
print server_path
serv.serve_forever()

gpio.cleanup()
