from google.appengine.ext import db
import re

testForNumber = re.compile('\d+')

def prefetchParent(entities, *props):
    fields = [(entity, prop) for entity in entities for prop in props]
    ref_keys = [prop.get_value_for_datastore(x) for x, prop in fields]
    ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
    for (entity, prop), ref_key in zip(fields, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
    return entities

def prefetch(entities):
	ref_keys = [x.parent_key() for x in entities if x.parent_key() is not None]
	ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
	ref_entities[None] = None
	for entity in entities:
		entity.parent_obj = ref_entities[entity.parent_key()]
	return entities

def get_string(string):
	return string.decode('utf-8')

def fillNoneString(string):
	if string is None:
		return ''
	return string

class Recipe(db.Model):
	chef = db.UserProperty()
	title = db.StringProperty()
	servesMin = db.IntegerProperty()
	servesMax = db.IntegerProperty()
	steps = db.TextProperty()
	date = db.DateTimeProperty(auto_now_add=True)

	def mostRecentPicture(self):
		lastCooked = self.instances.order('-created').get()
		if lastCooked is not None:
			return lastCooked.key().id()
		else:
			return None

	def updateIngredients(self, ingredients):
		for ingredient in self.ingredients:
			ingredient.delete()

		order = 1
		for ingredientText in ingredients:
			safeIngredientText = get_string(ingredientText)
			ingredient = RecipeIngredient(recipe = self)
			ingredient.order = order

			if len(safeIngredientText) > 0 and safeIngredientText[0] == '[':
				ingredient.amount = None
				ingredient.amountType = None
				ingredient.ingredient = fillNoneString(safeIngredientText)

			else:
				parts = safeIngredientText.split(' ', 3)
				if len(parts) >= 3:
					if len(parts) == 3 or not testForNumber.search(parts[1]):
						ingredient.amount = parts[0]
						ingredient.amountType = parts[1]
						ingredient.ingredient = ' '.join(parts[2:])
					else:
						ingredient.amount = parts[0] + ' ' + parts[1]
						ingredient.amountType = parts[2]
						ingredient.ingredient = ' '.join(parts[3:])
				else:
					ingredient.ingredient = safeIngredientText
				# fix any None values
				ingredient.amount = fillNoneString(ingredient.amount)
				ingredient.amountType = fillNoneString(ingredient.amountType)
				ingredient.ingredient = fillNoneString(ingredient.ingredient)

			ingredient.put()
			order += 1

	def updateReferences(self, links):
		for link in self.references:
			link.delete()

		for linkUri in links:
			safeLinkUri = get_string(linkUri)
			if (not 'http://' in safeLinkUri):
				safeLinkUri = 'http://' + safeLinkUri
			link = RecipeReference(recipe = self)
			link.link = safeLinkUri
			link.name = safeLinkUri.replace('http://', '', 1)
			cutName = len(link.name)
			if '/' in link.name:
				cutName = link.name.find('/')
			link.name = link.name[:cutName]
			link.put()

	def updateTags(recipe, tagList):
		for tag in tagList:
			print tag


class Tag(db.Model):
	name = db.StringProperty()
	htmlId = db.StringProperty()

class RecipeTag(db.Model):
	tag = db.ReferenceProperty(Tag, required=False, collection_name='recipes')
	recipe = db.ReferenceProperty(Recipe, required=False, collection_name='tags')

class RecipeInstance(db.Model):
	recipe = db.ReferenceProperty(Recipe, required=True, collection_name='instances')
	created = db.DateTimeProperty(auto_now_add=True)
	comments = db.StringProperty()
	picture = db.BlobProperty()
	# TODO: could add simple versioning recipeAsOfThisInstance = db.StringProperty()

class RecipeIngredient(db.Model):
	recipe = db.ReferenceProperty(Recipe, required=True, collection_name='ingredients')
	ingredient = db.StringProperty()
	amount = db.StringProperty()
	amountType = db.StringProperty()
	order = db.IntegerProperty()
	
	def isSectionHeading(self):
		return self.amount is None and self.amountType is None


class RecipeReference(db.Model):
	recipe = db.ReferenceProperty(Recipe, required=True, collection_name='references')
	name = db.StringProperty()
	link = db.LinkProperty()
