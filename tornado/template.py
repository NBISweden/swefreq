import jinja2
import tornado.template

class Jinja2Template(jinja2.Template):
    def generate(self, **kwargs):
        return self.render(**kwargs)

jinja2.Environment.template_class = Jinja2Template

class Jinja2TemplateLoader(tornado.template.BaseLoader):
    def __init__(self, *args, **kwargs):
        self._jinja2_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(''),
            )
        super(Jinja2TemplateLoader, self).__init__(**kwargs)

    def resolve_path(self, name, parent_path=None):
        return 'templates/' + name

    def _create_template(self, name):
        return self._jinja2_env.get_template(name)
