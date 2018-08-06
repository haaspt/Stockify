from setuptools import setup
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as file:
      long_description = file.read()

setup(name='Stockify',
      version='0.1',
      description='A simple application for stock data and portfolio tracking',
      url='https://github.com/haaspt/Stockify',
      author='Patrick Tyler Haas',
      author_email='patrick.tyler.haas@gmail.com',
      license='MIT',
      packages=['Stockify'],
      python_requires='>=3.6',
      install_requires=['requests'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
            'Programming Language :: Python :: 3.6'
      ],
      project_urls={
            'Bug Reports': 'https://github.com/haaspt/Stockify/issues',
            'Source': 'https://github.com/haaspt/Stockify'
      })