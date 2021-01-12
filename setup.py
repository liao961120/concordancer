from setuptools import setup

with open("README.md", encoding="utf-8") as f:
      long_description = f.read().strip()

setup(name='concordancer',
      version='0.1.12',
      description='Extract concordance lines from corpus with CQL',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/liao961120/concordancer',
      author='Yongfu Liao',
      author_email='liao961120@github.com',
      license='MIT',
      packages=['concordancer'],
      install_requires=['cqls', 'tabulate', 'falcon', 'falcon-cors'],
      #tests_require=['cqls'],
      zip_safe=False)
