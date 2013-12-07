import cgi
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
import django.utils.simplejson as json

from database import *
from config import *
from tools import *

class MainPage(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('index.html')

class OurStory(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('our-story.html')

class WeddingParty(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('wedding-party.html')

class CeremonyAndReception(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('ceremony-and-reception.html')

class RSVP(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('rsvp.html')
	def post(self):
		return
		self.checkUser()
		params = self.request.params
		rsvp = Response()
		rsvp.names = filter(lambda x: len(x) > 0, params.getall('name'))
		rsvp.coming = bool(params['coming'])
		rsvp.howMany = int(params['howMany'])
		rsvp.put()

class RequestSongs(BaseHandler):
	def getLinkForSong(self, song):
		self.checkUser()
		if song.startswith('http://') or song.startswith('https://'):
			return song 
		else:
			return 'http://www.google.com/search?q=' + song

	def getAllSongRequests(self):
		self.checkUser()
		return [song
			for songRequest in SongRequests.gql('Order By date DESC')
			for song in songRequest.songs
		]

	def get(self):
		self.checkUser()
		self.model['songs'] = self.getAllSongRequests()
		self.writeTemplate('request-songs.html')

	def post(self):
		return
		self.checkUser()
		params = self.request.params
		songRequests = SongRequests()
		songRequests.requester = params['requester']
		songRequests.requesterIpAddress = self.request.remote_addr
		songRequests.put()
		songList = filter(lambda x: len(x) > 0, params.getall('song'))
		for songText in songList:
			song = Song(songRequest = songRequests)
			song.link = self.getLinkForSong(songText)
			song.title = songText[:50]
			song.put()

		self.model['songs'] = self.getAllSongRequests()
		self.writeTemplate('requested-songs.html')

class VoteUp(BaseHandler):
	def post(self):
		return
		self.checkUser()
		songId = int(self.request.params['songId'])
		song = Song.get_by_id(songId)
		vote = SongVote(song=song)
		vote.voterIpAddress = self.request.remote_addr
		vote.put()
		self.writeResponse('(%s)' % song.votes.count())

class StuffToBring(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('stuff-to-bring.html')

class WhereToStay(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('where-to-stay.html')

class WhatToDo(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('what-to-do.html')

class SignOurGuestbook(BaseHandler):
	def get(self):
		self.checkUser()
		self.model['signatures'] = Guestbook.gql('Order By date DESC')
		self.writeTemplate('sign-our-guestbook.html')
	def post(self):
		return
		self.checkUser()
		params = self.request.params
		guestbook = Guestbook()
		guestbook.name = params['name']
		guestbook.note = params['note']
		guestbook.put()
		self.model['signatures'] = Guestbook.gql('Order By date DESC')
		self.writeTemplate('signatures.html')

class ContactUs(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('contact-us.html')

class YourAddress(BaseHandler):
	def get(self):
		self.checkUser()
		self.writeTemplate('your-address.html')
	def post(self):
		return
		self.checkUser()
		params = self.request.params
		address = Address()
		address.name = params['name']
		address.street = params['street']
		address.cityStateZip = params['cityStateZip']
		address.put()


application = webapp.WSGIApplication([
		# linked to:
		 ('/', MainPage)
		,('/our-story', OurStory)
		,('/wedding-party', WeddingParty)
		,('/ceremony-and-reception', CeremonyAndReception)
		,('/rsvp', RSVP)
		,('/request-songs', RequestSongs)
		,('/stuff-to-bring', StuffToBring)
		,('/where-to-stay', WhereToStay)
		,('/what-to-do', WhatToDo)
		,('/sign-our-guestbook', SignOurGuestbook)
		,('/contact-us', ContactUs)
		,('/actions/vote-up', VoteUp)
		# not linked to:
		,('/your-address', YourAddress)
	],
	debug=True
) if GlobalIsInDebug else webapp.WSGIApplication([
		# linked to:
		 ('/', MainPage)
		,('/our-story', OurStory)
		,('/wedding-party', WeddingParty)
		,('/ceremony-and-reception', CeremonyAndReception)
		,('/rsvp', RSVP)
		,('/request-songs', RequestSongs)
		,('/stuff-to-bring', StuffToBring)
		,('/where-to-stay', WhereToStay)
		,('/what-to-do', WhatToDo)
		,('/sign-our-guestbook', SignOurGuestbook)
		,('/contact-us', ContactUs)
		,('/actions/vote-up', VoteUp)
		# not linked to:
		,('/your-address', YourAddress)
	],
	debug=False
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

