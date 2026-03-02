import sys
from os import listdir, makedirs
from os.path import isdir, join, splitext, dirname
import markdown as md
from jinja2 import Environment, FileSystemLoader
import re

if len(sys.argv) < 4:
    print("Usage: python build.py CONTENT TEMPLATES OUTPUT")
    sys.exit(1)
CONTENT, TEMPLATES, OUTPUT = sys.argv[1:4]

class Content:
    """
    Represent a content page, convert the Markdown to HTML
    """
    def __init__(self, filename, output_folder=OUTPUT):
        self.filename = filename
        self.output_folder = output_folder

    def get_file_content(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def mdlink_to_htmllink(text):
        pattern = r'(<a href="[a-zA-Z0-9_-]*)\.md"'
        filtered = re.sub(pattern, r'\1.html"', text)
        return filtered

    def get_html(self):
        content = self.get_file_content()
        markd = md.Markdown(extensions=['extra', 'smarty', 'meta'])
        html_content = markd.convert(content)
        metadata = markd.Meta

        # Extract articles from content
        articles = self._extract_articles(content)

        # Render content in template, if template supports articles, will use articles instead
        env = Environment(loader=FileSystemLoader(TEMPLATES))
        template = env.get_template(metadata.get('template', ['base.html'])[0])
        rendered_html = template.render(
            content=Content.mdlink_to_htmllink(html_content),
            metadata=metadata,
            articles=articles
        )
        return rendered_html

    def _extract_articles(self, content):
        pattern = r'article::start(.*?)article::end'
        matches = re.findall(pattern, content, re.DOTALL)
        articles = []
        for match in matches:
            article_html = md.markdown(match.strip(), extensions=['extra', 'smarty'])
            articles.append(Content.mdlink_to_htmllink(article_html))
        return articles

    def output_html(self):
        rel_path = self.filename.replace(CONTENT, "")
        output_path = join(
            self.output_folder,
            splitext(rel_path)[0] + ".html"
        )
        makedirs(dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.get_html())


def recursive_render(folder, output_folder=OUTPUT):
    print(folder, output_folder)
    for name in listdir(folder):
        path = join(folder, name)
        out_path = join(output_folder, name)
        if isdir(path):
            makedirs(out_path, exist_ok=True)
            recursive_render(path + "/", out_path + "/")
        elif name.endswith('.md'):
            content = Content(path, output_folder)
            content.output_html()

if __name__ == "__main__":
    recursive_render(CONTENT)
