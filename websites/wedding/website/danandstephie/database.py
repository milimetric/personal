from google.appengine.ext import db

class Response(db.Model):
	names = db.StringListProperty()
	coming = db.BooleanProperty()
	howMany = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class Address(db.Model):
	name = db.StringProperty()
	street = db.StringProperty()
	cityStateZip = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class SongRequests(db.Model):
	requester = db.StringProperty()
	requesterIpAddress = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class Song(db.Model):
	link = db.StringProperty()
	title = db.StringProperty()
	songRequest = db.ReferenceProperty(SongRequests, required=True, collection_name='songs')

class SongVote(db.Model):
	song = db.ReferenceProperty(Song, required=True, collection_name='votes')
	voterIpAddress = db.StringProperty()

class Guestbook(db.Model):
	name = db.StringProperty()
	note = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)
