from google.appengine.ext.webapp.util import run_wsgi_app
from framework.router import WSGIRouter
from controllers.home import *
from controllers.recipe import *
from controllers.admin import *
from controllers.images import *

router = WSGIRouter()
router.connect('/', MainPage())
router.connect('/admin/{method}', Admin())
router.connect('/recipe/new', NewRecipe())
router.connect('/recipe/details/{id}', DetailRecipe())
router.connect('/recipe/edit/{id}', EditRecipe())
router.connect('/recipe/cook/save', InstanceRecipe())
router.connect('/recipe/cook/{id}', InstanceRecipe())
router.connect('/recipe/save', SaveRecipe())
router.connect('/recipe/list', AutocompleteList())

router.connect('/stored-images/{type}/{id}', ImageServer())

def main():
	run_wsgi_app(router)

if __name__ == "__main__":
	main()
