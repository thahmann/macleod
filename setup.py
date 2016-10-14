import distutils.core

distutils.core.setup(name='macleod',
                     version='0.9',
                     description='Ontology development framework',
                     url='https://github.com/thahmann/macleod',
                     author='Torsten Hahmann',
                     author_email='flyingcircus@example.com',
                     license='GPL3',
                     packages=['macleod'],
                     install_requires=['pyparsing==1.5.7'],
                     zip_safe=False)
