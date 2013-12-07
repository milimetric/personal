from framework.basecontroller import BaseHandler
from framework.result import Result
from database import *

class ImageServer(BaseHandler):
	def get(self, type, id):
		picture = ''
		if type == 'instance':
			picture = RecipeInstance.get_by_id(int(id)).picture

		self.response.body = picture
		self.response.cache_control = 'max-age=2592000, public'

