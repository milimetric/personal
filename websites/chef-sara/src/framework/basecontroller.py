import logging
import simplejson as json
from webob import exc, Request, Response
from framework.templating import *
from google.appengine.api import users

class BaseHandler(object):
	allowedMethods = ['get', 'post', 'put', 'head', 'delete']

	def __call__(self, wsgiEnvironment, startResponse):
		self.request = Request(wsgiEnvironment)
		self.response = Response(request = self.request, conditional_response = True)
		# make sure people are logged in
		self.user = users.get_current_user()
		if self.user:
			self.model = {
				'id': self.user.user_id(),
				'nickname': self.user.nickname(),
				'email': self.user.email(),
				'user': self.user,
				'logoutUrl': users.create_logout_url(self.request.path),
			}
		else:
			return self.redirect(users.create_login_url(self.request.path))(wsgiEnvironment, startResponse)

		try:
			self.handle()
			return self.response(wsgiEnvironment, startResponse)
		except exc.WSGIHTTPException, ex:
			return ex(wsgiEnvironment, startResponse)
		except Exception, ex:
			return self.handleException(ex)

	def handle(self):
		methodName = self.request.method.lower()
		method = getattr(self, methodName, None)
		kwargs = self.request.environ.get('router.args', {})
		if methodName not in self.allowedMethods or not method:
			raise exc.HTTPMethodNotAllowed()
		method(**kwargs)

	def handleException(self, exception):
		logging.exception('Unhandled Exception')
		return exc.HTTPInternalServerError('Server Error')

	def head(self, **kwargs):
		"""
		Default head handling method (allows sites like Digg to do a HEAD request
		"""
		method = getattr(self, 'get', None)
		if not method:
			raise exc.HTTPMethodNotAllowed()
		method(**kwargs)
		self.response.body = ''

	def redirect(self, location):
		return exc.HTTPFound(location = location)

	def renderTemplate(self, fileName):
		template = templateLookup.get_template(fileName)
		self.response.content_type = 'text/html'
		self.response.unicode_body = template.render(**self.model)

	def renderJson(self, obj):
		self.response.content_type = 'application/json'
		self.response.body = json.dumps(obj)

	def renderText(self, text):
		self.response.content_type = 'text/plain'
		self.response.body = text

