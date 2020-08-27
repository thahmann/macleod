from setuptools import setup
from setuptools import find_packages

setup(name='macleod',
    version='0.10',
    description='Ontology development framework',
    url='https://github.com/thahmann/macleod',
    author='Torsten Hahmann',
    author_email='torsten.hahmann@maine.edu',
    license='GPL3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyparsing',
        'configparser',
        'ply',
        'pywin32 ; platform_system=="Windows"',
        'wmi ; platform_system=="Windows"'
    ],
    extras_require={
        'GUI': ['PyQt5']
    },
    classifiers=["Programming Language :: Python :: 3.0"],
    entry_points={
        'console_scripts': [
            'check_consistency=macleod.scripts.check_consistency:main',
            'check_consistency_all=macleod.scripts.check_consistency_all:main',
            'check_nontrivial_consistency=macleod.scripts.check_nontrivial_consistency:main',
            'delete_output=macleod.scripts.delete_output:main',
            'prove_lemma=macleod.scripts.prove_lemma:main',
            'prove_lemma_all=macleod.scripts.prove_lemma_all:main',
            'clif_converter=macleod.scripts.clif_converter:main',
            'parse_clif=macleod.scripts.parser:main'
        ],
        'gui_scripts': [
            'macleod=macleod.gui.gui_beta.gui_main:main [GUI]'
        ]
    },
    zip_safe=False
)
