import jinja2
import tornado.template

class Jinja2Template(jinja2.Template):
    def generate(self, **kwargs):
        return self.render(**kwargs)

jinja2.Environment.template_class = Jinja2Template

class Jinja2TemplateLoader(tornado.template.BaseLoader):
    def __init__(self, root_dir=None, *args, **kwargs):
        self._jinja2_env = jinja2.Environment(
                block_start_string    = '[%',
                block_end_string      = '%]',
                variable_start_string = '[[',
                variable_end_string   = ']]',
                comment_start_string  = '[#',
                comment_end_string    = '#]'
            )
        if root_dir:
            self._jinja2_env.loader = jinja2.FileSystemLoader(root_dir)
        else:
            self._jinja2_env.loader = jinja2.FileSystemLoader()
        super().__init__(**kwargs)

    def resolve_path(self, name, parent_path=None):
        return name

    def _create_template(self, name):
        return self._jinja2_env.get_template(name)
