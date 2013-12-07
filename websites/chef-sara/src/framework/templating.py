from mako.template import Template
from mako.lookup import TemplateLookup

templateLookup = TemplateLookup(directories = ['templates'])
templateCache = {}

def mako_patch_memcache():
	"""
	A function to patch mako to store compiled template in memcache.
	In debug mode(config.debug == True), It never store them in memcache.
	NOTE: thanks to the aha framework for this idea - It turns out local memory gets wiped pretty often, so keeping around the memcache idea to load test both
	"""
	from mako.template import Lexer, codegen, types
	from google.appengine.api import memcache
	cvid = os.environ.get('CURRENT_VERSION_ID','')
	
	def _compile_text(template, text, filename):
		identifier = template.module_id
		no_cache = identifier.startswith('memory:') or config.debug
		cachekey = 'makosource:%s:%s' % (str(cvid), str(identifier))
		if not no_cache:
			source = memcache.get(cachekey)
		if no_cache or source is None:
			lexer = Lexer(text, filename, 
						  disable_unicode = template.disable_unicode, 
						  input_encoding = template.input_encoding,
						  preprocessor = template.preprocessor)
			node = lexer.parse()
			source = codegen.compile(node, template.uri, filename,
							 default_filters = template.default_filters, 
							 buffer_filters = template.buffer_filters, 
							 imports = template.imports)
			if not no_cache:
				memcache.set(cachekey, source)
				logging.debug("Store mako template: "+cachekey)
		cid = identifier
		if isinstance(cid, unicode):
			cid = cid.encode()
		module = types.ModuleType(cid)
		code = compile(source, cid, 'exec')
		exec code in module.__dict__, module.__dict__
		return (source, module) 

	def _compile_module_file(template, text, filename, outputpath):
		_compile_text(template, text, filename)
	
	template._compile_text = _compile_text
	template._compile_module_file = _compile_module_file

def mako_patch_local_memory():
	"""
	A function to patch mako to store compiled template in memcache.
	In debug mode(config.debug == True), It never store them in memcache.
	NOTE: thanks to the aha framework for this idea - modified to store in local memory
			It turns out local memory gets wiped pretty often, so keeping around the memcache idea to load test both
	"""
	from mako.template import Lexer, codegen, types
	from google.appengine.api import memcache
	cvid = os.environ.get('CURRENT_VERSION_ID','')
	
	def _compile_text(template, text, filename):
		identifier = template.module_id
		no_cache = identifier.startswith('memory:') or config.debug
		cachekey = 'makosource:%s:%s' % (str(cvid), str(identifier))
		if not no_cache:
			if cachekey in templateCache:
				source = templateCache[cachekey]
		if no_cache or source is None:
			lexer = Lexer(text, filename, 
						  disable_unicode = template.disable_unicode, 
						  input_encoding = template.input_encoding,
						  preprocessor = template.preprocessor)
			node = lexer.parse()
			source = codegen.compile(node, template.uri, filename,
							 default_filters = template.default_filters, 
							 buffer_filters = template.buffer_filters, 
							 imports = template.imports)
			if not no_cache:
				templateCache[cachekey] = source
				logging.debug("Store mako template: "+cachekey)
		cid = identifier
		if isinstance(cid, unicode):
			cid = cid.encode()
		module = types.ModuleType(cid)
		code = compile(source, cid, 'exec')
		exec code in module.__dict__, module.__dict__
		return (source, module) 

	def _compile_module_file(template, text, filename, outputpath):
		_compile_text(template, text, filename)
	
	template._compile_text = _compile_text
	template._compile_module_file = _compile_module_file

# perform patches to mako
try:
	mako_patch_local_memory()
except:
	pass
	
