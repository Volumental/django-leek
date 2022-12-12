import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


with open('README.md') as f:
    README = f.read()


setup(
    name='django-leek',
    version='1.0.4',
    packages=find_packages(exclude=['test_app']),
    install_requires=['django>=1.11'],
    include_package_data=True,
    license='MIT License',
    description='A simple Django app to offload tasks from main web server',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/Volumental/django-leek',
    author='Volumental',
    author_email='maintainer@volumental.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
