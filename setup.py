# setup.py

from setuptools import setup, find_packages

setup(
    name='netflix',
    version='1.0.0',
    description='Visualisation Netflix-Transformation over time',
    author='Boris Lauper, Sven Rudbog, Elias Martinelli',
    author_email='boris.lauper@stud.hslu.ch, sven.rudbog@stud.hslu.ch, elias.martinelli@stud.hslu.ch',
    packages=find_packages(include=['netflix', 'netflix.*']),
    install_requires=[
        'tensorflow>=2.8',
        'keras',
        'scikit-learn',
        'pandas',
        'numpy',
        'pandas_datareader',
        'fastapi',
        'uvicorn[standard]',
        'joblib',
        'streamlit',
        'python-dotenv',
        'keras-tuner',
        'matplotlib',
        'requests'
    ],
    include_package_data=True,
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts': [
            'run-predictor=netflix.__main__:main',
        ]
    }
)
