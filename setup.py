# setup.py
from setuptools import setup, find_packages

# Collect and merge all requirements for dev
req_files = ['src/frontend/requirements_frontend.txt']
requirements = []
for rfile in req_files:
    with open(rfile, encoding="UTF-8") as f:
        content = f.readlines()
    requirements += [x.strip() for x in content if x.strip() not in requirements]

setup(
    name='TheNetflixStory',
    version='1.0.0',
    description='The shift from traditional cinema to the series ecosystem',
    author='Boris Lauper, Sven Rudbog, Elias Martinelli',
    author_email='boris.lauper@stud.hslu.ch, sven.rudbog@stud.hslu.ch,'
                 'elias.martinelli@stud.hslu.ch',
    packages=find_packages(where='src'), # Damit pip install -e . die Module findet.
    package_dir={'': 'src'},             # Damit setuptools bei späterer Paketierung
                                         # die Module findet.
    install_requires=requirements,
    python_requires='>=3.10.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts': [
            'run-story=netflix.__main__:main',
        ]
    }
)
