from setuptools import setup

README = '''
Async ClickHouse ORM.

More information available on read the doc: https://github.com/qvp/aiochorm
'''

setup(
    name='aiochorm',
    version='0.1.11',
    packages=['aiochorm'],
    description='Async ClickHouse ORM.',
    long_description=README,
    author='Alexander Kuzmenko',
    author_email='mail@alexanderkuzmenko.com',
    url='https://github.com/qvp/aiochorm',
    download_url='',
    license='MIT',
    install_requires=[
        'aioch==0.0.1',
        'infi.clickhouse-orm==1.2.0',
    ]
)
