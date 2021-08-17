try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


config = {
    'description': 'My Project',
    'author': 'Lars Vogt',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_mail': 'lars.m.vogt@googlemail.com',
    'version': '0.16',
    'install_requirements': ['pytest', 'Flask', 'neo4j', 'habanero', 'django', 'json', 'html', 'uuid', 'datetime', 'crossref_commons.retrieval', 'ast', 're'],
    'packages': ['KGBB'],
    'scripts': [],
    'name': 'Knowledge-Graph-Building-Blocks'
}

setup(**config)
