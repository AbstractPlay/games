import os
import json
from base64 import b64decode
import cherrypy

#PID file
pidfile = os.getenv('ABSTRACTPLAY_PIDFILE', "logs/server.pid")
from cherrypy.process.plugins import PIDFile
PIDFile(cherrypy.engine, pidfile).subscribe()

#template folder
templatedir = os.getenv('ABSTRACTPLAY_TEMPLATES', "/home/protected/server/templates")
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(templatedir))

#secure the headers
def secureheaders():
    headers = cherrypy.response.headers
    headers['X-Frame-Options'] = 'DENY'
    headers['X-XSS-Protection'] = '1; mode=block'
    # headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self' 'unsafe-inline' connect.facebook.net apis.google.com; connect-src 'self'; img-src 'self' data: www.facebook.com apis.google.com; style-src 'self' 'unsafe-inline'; child-src 'self' accounts.google.com staticxx.facebook.com www.facebook.com;"
    headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; child-src 'self';"

cherrypy.tools.secureheaders = cherrypy.Tool('before_finalize', secureheaders, priority=60)

#Pull in the various game and AI modules
from lib.games.ithaka import Ithaka

class Root(object):
	exposed = True

	def __init__(self):
		self.ithaka = Ithaka()

	def OPTIONS(self):
		return None

root = Root()

if __name__ == '__main__':
	cherrypy.config.update("server.conf")
	cherrypy.tree.mount(root, '/', "server.conf")
	cherrypy.engine.start()
	cherrypy.engine.block()
