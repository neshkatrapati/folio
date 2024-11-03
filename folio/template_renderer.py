from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2 import BaseLoader, TemplateNotFound
from os.path import join, exists, getmtime

PROMPTS_DIR = "folio/prompts"
class FolioTemplateLoader(BaseLoader):

    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        path = join(self.path, template)
        if not exists(path):
            raise TemplateNotFound(template)
        mtime = getmtime(path)
        with open(path) as f:
            source = f.read()
        return source, path, lambda: mtime == getmtime(path)


def render_prompt(prompt_path:str, data:dict) -> str:
    loader = FolioTemplateLoader(PROMPTS_DIR)
    env = Environment(loader=loader, autoescape=select_autoescape())
    template = env.get_template(prompt_path)
    return template.render(data)