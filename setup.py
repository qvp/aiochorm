from setuptools import setup

README = '''
Quick import CSV data into database via command line or code.

This package provides a console command for quickly importing data into the database as well as API for quickly developing a code for importing CSV.

More information available on read the doc: https://github.com/qvp/django-import-csv
'''

setup(
    name='django-import-csv',
    version='0.1.10',
    packages=['import_csv', 'import_csv.management.commands'],
    description='Quick import CSV data into database via command line or code.',
    long_description=README,
    author='Alexander Kuzmenko',
    author_email='alexanderkuzmenko.com@gmail.com',
    url='https://github.com/qvp/django-import-csv/',
    download_url='',
    license='MIT',
    install_requires=[
        'Django>=2.0',
    ]
)
