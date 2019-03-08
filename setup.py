from setuptools import setup

setup(name='macleod',
      version='0.9',
      description='Ontology development framework',
      url='https://github.com/thahmann/macleod',
      author='Torsten Hahmann',
      author_email='torsten.hahmann@maine.edu',
      license='GPL3',
      packages=['macleod'],
      install_requires=['pyparsing==2.1.10',
                        'configparser',
                        'owlready',
                        'ply'],
      classifiers=["Programming Language :: Python :: 3.0"],
      zip_safe=False)
