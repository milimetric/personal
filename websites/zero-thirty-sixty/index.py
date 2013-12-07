#****************************************
#	Imports
#****************************************
import webapp2
import logging
import json
from webapp2_extras import routes
from google.appengine.ext import db
from webapp2_extras import jinja2
from google.appengine.api import users
 

#****************************************
#	Database
#****************************************
class Learnable(db.Model):
	imageUri = db.StringProperty()
	def toDictionary(self):
		return {
			'key': str(self.key()),
			'imageUri': self.imageUri
		}

class UserLearned(db.Model):
	user = db.UserProperty()
	learnable = db.ReferenceProperty(Learnable, collection_name="users")
	learnedAfterThirty = db.BooleanProperty()
	def toDictionary(self):
		return {
			'key': str(self.key()),
			'user': str(self.user),
			'learnableKey': str(self.learnable.key()),
			'learnedAfterThirty': str(self.learnedAfterThirty)
		}


#****************************************
#	BaseHandler
#****************************************
class BaseHandler(webapp2.RequestHandler):
	def auth(self):
		self.user = users.get_current_user()
		self.model = {}
		if self.user:
			self.model['id'] = self.user.user_id()
			self.model['nickname'] = self.user.nickname()
			self.model['email'] = self.user.email()
			self.model['logoutUrl'] = users.create_logout_url(self.request.path)
			return True
		else:
			self.redirect(users.create_login_url(self.request.path))
			return False

	@webapp2.cached_property
	def jinja2(self):
		# Returns a Jinja2 renderer cached in the app registry.
		return jinja2.get_jinja2(app = self.app)

	def renderTemplate(self, _template):
		# Renders a template and writes the result to the response.
		self.response.headers['Content-Type'] = 'text/html'
		rv = self.jinja2.render_template(_template, **self.model)
		self.response.write(rv)

	def renderJson(self, jsonString):
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(jsonString))


#****************************************
#	Handlers
#****************************************
class HomeHandler(BaseHandler):
	def get(self):
		if self.auth():
			self.renderTemplate('index.html')

class MainHandler(BaseHandler):
	def get(self):
		if self.auth():
			results = dict(
				learnables = [r.toDictionary() for r in Learnable.all().fetch(1000)],
				userLearneds = [r.toDictionary() for r in UserLearned.gql('WHERE user=:1', self.user)]
			)
			self.renderJson(results)

class LearnHandler(BaseHandler):
	def post(self):
		if self.auth():
			r = self.request
			learn = UserLearned()
			learn.user = self.user
			learnableKey = db.Key(r.get('learnableKey'))
			learn.learnable = Learnable.get(learnableKey)
			learn.learnedAfterThirty = r.get('learnedAfterThirty') == 'true'
			learn.put()
			self.renderJson(dict(key = str(learn.key())))

class UnlearnHandler(BaseHandler):
	def post(self):
		if self.auth():
			r = self.request
			key = db.Key(r.get('key'))
			userLearned = UserLearned.get(key)
			userLearned.delete()

class AddLearnableHandler(BaseHandler):
	def post(self):
		if self.auth():
			r = self.request
			learnable = Learnable()
			learnable.imageUri = r.get('imageUri')
			learnable.put()
			self.renderJson(learnable.toDictionary())


#****************************************
#	Routing and HTTP Exceptions
#****************************************
routing = webapp2.WSGIApplication([
    webapp2.Route(r'/',        handler = HomeHandler, name = 'home', methods=['GET']),
    webapp2.Route(r'/main',    handler = MainHandler, name = 'main', methods=['GET']),
    webapp2.Route(r'/learn',   handler = LearnHandler, name = 'learn', methods=['POST']),
    webapp2.Route(r'/unlearn', handler = UnlearnHandler, name = 'unlearn', methods=['POST']),
    webapp2.Route(r'/add',     handler = AddLearnableHandler, name = 'add', methods=['POST']),
], debug=True)

# jinja2 configuration
if not routing.debug:
	jinja2.default_config['environment_args']['auto_reload'] = False
jinja2.default_config['environment_args']['line_statement_prefix'] = '#'

def handle_404(request, response, exception):
	logging.exception(exception)
	response.write('Oops! I could swear this page was here!')
	response.set_status(404)

def handle_500(request, response, exception):
	logging.exception(exception)
	response.write('A server error occurred!')
	response.set_status(500)

routing.error_handlers[404] = handle_404
routing.error_handlers[500] = handle_500

