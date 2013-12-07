from cgi import FieldStorage
from framework.basecontroller import BaseHandler
from framework.result import Result
from database import *
from google.appengine.api import images
from google.appengine.api import users
#TODO: hard-coding URIs is bad, create a "make route" method
	
def canEdit(self, recipe):
	return users.is_current_user_admin() or self.user == recipe.chef

class NewRecipe(BaseHandler):
	def get(self):
		self.model['tags'] = Tag.gql("Order By date DESC")
		self.model['recipe'] = Recipe()
		self.renderTemplate('editRecipe.html')

class DetailRecipe(BaseHandler):
	def get(self, id):
		recipe = Recipe.get_by_id(int(id))
		self.model['recipe'] = prefetch([recipe])[0]
		self.renderTemplate('recipeDetails.html')

class EditRecipe(BaseHandler):
	def get(self, id):
		recipe = Recipe.get_by_id(int(id))
		if canEdit(self, recipe):
			recipe.steps = recipe.steps.replace('<br/>', '\n')
			self.model['recipe'] = prefetch([recipe])[0]
			self.model['tags'] = Tag.gql("Order By date DESC")
			self.renderTemplate('editRecipe.html')
		else:
			raise self.redirect('/recipe/details/' + id)

class SaveRecipe(BaseHandler):
	def post(self):
		params = self.request.params
		id = params['id']
		isEdit = len(id) > 0
		ingredients = params['ingredients'].split('\n')
		tags = params.getall('tags')
		links = params.getall('links')

		recipe = None
		if isEdit:
			recipe = Recipe.get_by_id(int(id))
			if not canEdit(self, recipe):
				raise self.redirect('/recipe/details/' + id)
		else:
			recipe = Recipe()
			recipe.chef = self.user

		recipe.title = params['title']
		recipe.servesMin = int(params['servesMin'])
		recipe.servesMax = int(params['servesMax'])
		recipe.steps = get_string(params['steps'].replace('\n', '<br/>'))

		recipe.put()
		recipe.updateIngredients(ingredients)
		recipe.updateReferences(links)
		recipe.updateTags(tags)

		id = str(recipe.key().id())
		raise self.redirect('/recipe/details/' + id)

class InstanceRecipe(BaseHandler):
	def get(self, id):
		recipe = Recipe.get_by_id(int(id))
		self.model['recipe'] = prefetch([recipe])[0]
		self.renderTemplate('recipeInstances.html')

	def post(self):
		params = self.request.params
		id = params['id']
		recipe = Recipe.get_by_id(int(id))
		recipeInstance = RecipeInstance(recipe=recipe)
		recipeInstance.comments = params['comments']
		postedImage = self.request.POST['image']
		if postedImage is not None and postedImage is not '':
			resizedImage = images.resize(postedImage.file.getvalue(), 600, 600, images.JPEG)
			recipeInstance.picture = db.Blob(resizedImage)
			recipeInstance.pictureExists = True
		recipeInstance.put()
		raise self.redirect('/recipe/cook/' + id)

class AutocompleteList(BaseHandler):
	def get(self):
		allRecipes = []
		for recipe in Recipe.gql("Order By title"):
			mostRecentPicture = recipe.mostRecentPicture()
			allRecipes.append({
				'label' : recipe.title,
				'details' : '/recipe/details/' + str(recipe.key().id()),
				'picture': '/stored-images/instance/' + str(mostRecentPicture) if mostRecentPicture else ''
			})
		self.renderJson(allRecipes)


