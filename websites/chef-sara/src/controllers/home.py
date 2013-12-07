from framework.basecontroller import BaseHandler
from framework.result import Result
from database import *

class MainPage(BaseHandler):
	def get(self):
		self.model['recipes'] = Recipe.gql("Order By date DESC LIMIT 10")
		self.renderTemplate('index.html')

