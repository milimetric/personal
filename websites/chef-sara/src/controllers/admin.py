from framework.basecontroller import BaseHandler
from framework.result import Result
from database import *

class Admin(BaseHandler):
	def get(self, method):
		if self.user.is_current_user_admin():
			if method == 'upgradeRecipeInstance':
				instances = RecipeInstance.all()
				for instance in instances:
					instance.pictureExists = instance.picture is not None
					instance.put()
			self.renderTemplate('master.html')

