try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'PyBiotools is a package to agregate a collection of tools '
                   'and scripts commonly used on LGHM and Neuro bioinformatics '
                   'laboratories',
    'author': 'André M. Ribeiro dos Santos',
    'url': '',
    'download_url': '',
    'author_email': 'andremrsantos@neuro.ufrn.br',
    'version': '1.0.1',
    'install_requires': ['nose'],
    'packages': ['pybiotools'],
    'scripts': ['pybiotools'],
    'name': 'pybiotools'
}

setup(**config)
