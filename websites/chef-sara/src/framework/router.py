import re

class WSGIRouter(object):
    def __init__(self):
        self.routes = []

    def connect(self, template, handler, **kwargs):
        """Connects URLs matching a template to a handler application.

        Args:
            template: A template string, consisting of literal text and template
                expressions of the form {label[: regex]}, where label is the mandatory
                name of the expression, and regex is an optional regular expression.
            handler: A WSGI application to execute when the template is matched.
            **kwargs: Additional keyword arguments to pass along with those parsed
                from the template.
        """
        route_re = re.compile(template_to_regex(template))
        self.routes.append((route_re, handler, kwargs))

    def __call__(self, environment, start_response):
        for regex, handler, kwargs in self.routes:
            match = regex.match(environment['PATH_INFO'])
            if match:
                environment['router.args'] = dict(kwargs)
                environment['router.args'].update(match.groupdict())
                return handler(environment, start_response)

var_regex = re.compile(r'''
    \{          # The exact character "{"
    (\w+)       # The variable name (restricted to a-z, 0-9, _)
    (?::([^}]+))? # The optional :regex part
    \}          # The exact character "}"
    ''', re.VERBOSE)

def template_to_regex(template):
    regex = ''
    last_pos = 0
    for match in var_regex.finditer(template):
        regex += re.escape(template[last_pos:match.start()])
        var_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (var_name, expr)
        regex += expr
        last_pos = match.end()
    regex += re.escape(template[last_pos:])
    regex = '^%s$' % regex
    return regex
