<!-- ![Python package](https://github.com/viralogic/py-enumerable/workflows/Python%20package/badge.svg) -->

# LINQ Python #

This project is based on viralogic's repository [py_linq](https://github.com/viralogic/py-enumerable)

LINQ (Language Integrated Query) is a popular querying language available in .NET. This library ports the language so
that developers can query collections of objects using the same syntax. This library would be useful for Python developers with experience using the expressiveness and power of LINQ.

## Usage

To access the LINQ functions an iterable needs to be wrapped by the Enumerable

```python
from py_linq import Enumerable
clist = [0,1,2,3,4,5]
Enumerable(clist).order_by(lambda x: x).take(2).where(lambda x: x.x > 0).to_list() 
```

## Documentation ##

Please visit the original project's documentation [site](https://viralogic.github.io/py-enumerable)




