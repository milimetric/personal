import os
import random
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template

class BaseHandler(webapp.RequestHandler):
	def __init__(self):
		self.user = None
		self.model = {}

	def checkUser(self):
		self.user = users.get_current_user()
		if self.user:
			self.model = {
				'nickname': self.user.nickname(),
				'url': users.create_logout_url(self.request.uri),
				'url_linktext': 'Logout'
			}
		else:
			self.redirect(users.create_login_url(self.request.uri))

	def writeTemplate(self, templatePath):
		self.model['random'] = random.randint(1,4)
		path = os.path.join(os.path.dirname(__file__), templatePath)
		self.response.out.write(template.render(path, self.model))

	def writeResponse(self, html):
		self.response.out.write(html)
