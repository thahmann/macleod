from setuptools import setup

setup(name='macleod',
      version='0.9',
      description='Ontology development framework',
      url='https://github.com/thahmann/macleod',
      author='Torsten Hahmann',
      author_email='flyingcircus@example.com',
      license='GPL3',
      packages=['macleod', 'macleod.dl', 'macleod.logical', 'macleod.parsing'],
      install_requires=['pyparsing==2.1.10',
                        'configparser',
                        'PLY'],
      classifiers=["Programming Language :: Python :: 3.6+"],
      zip_safe=False)
