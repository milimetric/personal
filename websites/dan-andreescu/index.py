import cgi
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import django.utils.simplejson as json
# import json
# writer = json.JsonWriter()
# reader = json.JsonReader()

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^airplane/(\d+)/$', ''),
#    (r'^articles/2003/$', 'news.views.special_case_2003'),
#    (r'^articles/(\d{4})/$', 'news.views.year_archive'),
#    (r'^articles/(\d{4})/(\d{2})/$', 'news.views.month_archive'),
#    (r'^articles/(\d{4})/(\d{2})/(\d+)/$', 'news.views.article_detail'),
)


class AirplaneGame(db.Model):
	author = db.UserProperty()
	joiner = db.UserProperty()
	name = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	def get_id(self):
		return self.key().id()
	id = property(get_id)

class Puzzle(db.Model):
	author = db.UserProperty()
	name = db.StringProperty()
	lightsOn = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class Pattern(db.Model):
	author = db.UserProperty()
	name = db.StringProperty()

class PatternObservableFact(db.Model):
	pattern = db.ReferenceProperty(Pattern, required=True, collection_name='facts')
	name = db.StringProperty()

class PatternFactOccurrence(db.Model):
	pattern = db.ReferenceProperty(Pattern, required=True, collection_name='occurrences')
	observableFact = db.ReferenceProperty(PatternObservableFact, required=True, collection_name='factOccurrences')
	observableFactQuantity = db.StringProperty()
	timeOfDay = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)



def userModel(requestUri):
	user = users.get_current_user()
	nickname = ''
	if user:
		url = users.create_logout_url(requestUri)
		url_linktext = 'Logout'
		nickname = user.nickname()
	else:
		url = users.create_login_url(requestUri)
		url_linktext = 'Login'

	model = {
		'nickname': nickname,
		'url': url,
		'url_linktext': url_linktext
	}
	return model

def writeResponse(templatePath, self, model):
	path = os.path.join(os.path.dirname(__file__), templatePath)
	self.response.out.write(template.render(path, model))

class MainPage(webapp.RequestHandler):
	def get(self):
		model = userModel(self.request.uri)
		writeResponse('index.html', self, model)

class LightsOutPage(webapp.RequestHandler):
	def get(self):
		model = userModel(self.request.uri)
		puzzles = Puzzle.gql("Order By date DESC")
		model['puzzles'] = puzzles

		writeResponse('games/lightsOut.html', self, model)

class AirplanePage(webapp.RequestHandler):
	def get(self):
		model = userModel(self.request.uri)
		user = users.get_current_user()
		if user:
			airplaneGames = db.GqlQuery("SELECT * FROM AirplaneGame WHERE author = :1 ORDER By date DESC", user)
			model["airplaneGames"] = airplaneGames;

		writeResponse('games/airplane.html', self, model)

class PatternPage(webapp.RequestHandler):
	def get(self):
		model = userModel(self.request.uri)
		user = users.get_current_user()
		if user:
			patterns = db.GqlQuery("SELECT * FROM Pattern WHERE author = :1 ORDER By name ASC", user)
			model["patterns"] = patterns;

		writeResponse('games/patterns.html', self, model)

class SavePuzzleAction(webapp.RequestHandler):
	def post(self):
		params = json.loads(self.request.body)
		puzzle = Puzzle()
		puzzle.name = params['name']
		puzzle.lightsOn = params['lightsOn']
		if users.get_current_user():
			puzzle.author = users.get_current_user()
		puzzle.put()

		puzzles = Puzzle.gql("Order By date DESC")
		model = {
			'puzzles': puzzles
		}

		writeResponse('games/puzzles.html', self, model)

class StartGameAction(webapp.RequestHandler):
	def post(self):
		params = json.loads(self.request.body)
		model = userModel(self.request.uri)
		airplane = AirplaneGame()
		airplane.name = params['Name']
		if users.get_current_user():
			airplane.author = users.get_current_user()
		airplane.put()

class StartPatternAction(webapp.RequestHandler):
	def post(self):
		params = json.loads(self.request.body)
		model = userModel(self.request.uri)
		pattern = Pattern()
		pattern.name = params['Name']
		user = users.get_current_user()
		if user:
			pattern.author = users.get_current_user()
		pattern.put()

		if user:
			patterns = db.GqlQuery("SELECT * FROM Pattern WHERE author = :1 ORDER By name ASC", user)
			model['patterns'] = patterns;
		writeResponse('games/patternList.html', self, model);

class GetPatternAction(webapp.RequestHandler):
	def post(self):
		params = json.loads(self.request.body)
		model = userModel(self.request.uri)

		user = users.get_current_user()
		if user:
			key = params['key']
			pattern = db.get(db.Key(key))
			model['facts'] = pattern.facts
			model['occurrences'] = pattern.occurrences
			model['pattern'] = pattern

		writeResponse('games/patternDetail.html', self, model);

class AddFactAction(webapp.RequestHandler):
	def post(self):
		params = json.loads(self.request.body)
		model = userModel(self.request.uri)

		user = users.get_current_user()
		if user:
			key = params['ParentKey']
			pattern = db.get(db.Key(key))

			fact = PatternObservableFact(pattern=pattern)
			fact.name = params['Name']
			fact.put()

			model['facts'] = pattern.facts
			model['occurrences'] = pattern.occurrences
			model['pattern'] = pattern

		writeResponse('games/patternDetail.html', self, model);

class AddOccurrenceAction(webapp.RequestHandler):
	def post(self):
		params = json.loads(self.request.body)
		model = userModel(self.request.uri)

		user = users.get_current_user()
		if user:
			key = params['ParentKey']
			pattern = db.get(db.Key(key))

			factSelected = db.get(db.Key(params['Fact']))
			occurrence = PatternFactOccurrence(pattern=pattern, observableFact=factSelected)
			occurrence.observableFactQuantity = params['Quantity']
			occurrence.timeOfDay = params['TimeOfDay']
			occurrence.put()

			model['facts'] = pattern.facts
			model['occurrences'] = pattern.occurrences
			model['pattern'] = pattern

		writeResponse('games/patternDetail.html', self, model);

class JoinGameAction(webapp.RequestHandler):
	def post(self):
		model = userModel(self.request.uri)
		
		writeResponse('games/airplane.html', self, model)
		

application = webapp.WSGIApplication(
                                     [('/', MainPage),
									  ('/lightsOut', LightsOutPage),
									  ('/airplane', AirplanePage),
									  ('/patterns', PatternPage),
                                      ('/save', SavePuzzleAction),
									  ('/ajax/StartGame', StartGameAction),
									  ('/ajax/GetPattern', GetPatternAction),
									  ('/ajax/StartPattern', StartPatternAction),
									  ('/ajax/AddFact', AddFactAction),
									  ('/ajax/AddOccurrence', AddOccurrenceAction)
									 ],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

