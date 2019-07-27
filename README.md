# django-import-csv
Quick import CSV data into database via command line or code.

## Installation
To install, simply use pip
```
pip install django-import-csv
```
and add import_csv into django's settings
```python
INSTALLED_APPS = [
    # ...
    'import_csv',
]
```

## Import via command line
```bash
python manage.py import-csv file fields model [--error_file]
```
For example import products to product table:
```bash
python manage.py import-csv path/products.csv ,,title,price,,image shop.models.Product
```
The products.csv file looks like this:
```csv
1, fruits,     Apple,  $0.75, green,  apple.png
2, Berries,    Banana, $0.60, yellow, banana.png
3, Vegetables, Potato, $1.1,  brown,  potato.png
```
The model shop.models.Product:
```python
class Product(Model):
    title = models.CharField()
    price = models.DecimalField()
    image = models.ImageField()
    
    def import_csv(self, attrs):
        """ Special method for save CSV row """
        # attrs is a dict: {'title': 'Apple', 'price': '$0.75', 'image': 'apple.png'}
        # save row here and return True or False
        return True  # False for send row to errors file
```

## Optional fields, default value, value parser
You can set advanced field settings in a special class
```python
from import_csv.rows import Row
from import_csv.fields import Field


class ProductRow(Row):
    title = Field(index=2)
    price = Field(index=3, parser='parse_price')
    image = Field(5, blank=True, default='no-img.png')
    
    def parse_price(self, value):
        return value[1:]
```
and set path to row class instead fields
```bash
python manage.py import-csv path/products.csv shop.rows.ProductRow shop.models.Product
```

## Save CSV rows with errors
Strings that failed validation or that failed to save are sent to a error file.
```bash
python manage.py import-csv path/products.csv shop.rows.ProductRow shop.models.Product --error_file=files/errors/fruits.csv
```

## Import from code
```python
from import_csv.importers import Importer

importer = Importer(file_path, row_class, model_class)

for error_line in importer.run():
    # save wrong lines to file or etc
    pass
```
