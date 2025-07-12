from setuptools import setup, find_packages

setup(
    name='ezesri',
    version='0.3.0',
    packages=find_packages(),
    description='A lightweight Python package for extracting data from Esri REST API endpoints.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Justin Myles',
    author_email='justin@myles.com',
    url='https://github.com/stiles/ezesri',
    keywords=['esri', 'gis', 'geospatial', 'arcgis', 'rest-api'],
    install_requires=[
        'requests',
        'geopandas',
        'pandas',
        'click',
        'tqdm',
        'fiona',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'ezesri=ezesri.cli:cli',
        ],
    }
) 