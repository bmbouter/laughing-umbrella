from setuptools import setup

setup(
    name='laughing-umbrella',
    version='0.1a1',
    homepage='',
    description='Github Issue Classifier',
    url='',
    author='Brian Bouterse',
    author_email='bmbouter@gmail.com',
    license='',
    packages=['laughing_umbrella'],
    install_requires=[
        'aiohttp',
        'Django',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
