import argparse
import datetime
from pathlib import Path

import jinja2

class Jinja2Renderer:
    def __init__(self, directory):
        self.env = jinja2.Environment(autoescape=True,
                                      block_start_string='[%',
                                      block_end_string='%]',
                                      variable_start_string='[[',
                                      variable_end_string=']]',
                                      comment_start_string='[#',
                                      comment_end_string='#]',
                                      loader=jinja2.FileSystemLoader(str(directory)))

    def render(self, file, **kwargs):
        template = self.env.get_template(str(file))
        return template.render(**kwargs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--basedir", dest='basedir', required=True)
    parser.add_argument("-s", "--source", dest='src', required=True)
    parser.add_argument("-d", "--develop", dest='develop', required=False, action='store_true')
    args = parser.parse_args()

    src = Path(args.src).relative_to(args.basedir)

    renderer = Jinja2Renderer(args.basedir)
    res = renderer.render(src,
                          develop=args.develop,
                          version=datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))
    print(res)


if __name__ == '__main__':
    main()
