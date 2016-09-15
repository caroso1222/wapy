#Wapy      
Wapy is a Python wrapper for the Walmart Open API.

##Features
* Easy to use, object oriented interface to the Walmart Open API. (*Products and Reviews are retrieved as objects*)
* Get ready to use, parsed attributes. *e.g. prices as `float`, no strings with escaped html entities, numbers as `int`.*
* Full support for Walmart Search API, Product Recommendation API, Post Browsed Products API, Trending API and more.
* Get all responses with `richAttributes='true'` by default. *This lets you get weight and dimensions right off the shelf.*
* Proper error handling according to original Walmart API documentation
* Helper functions such as `bestseller_products()` and more from the Special Feeds section.
* Silently fails when attribute not found in response
* Fully documented source code

##Requirements
Before using Wapy, you want to make sure you have `requests` installed and a Walmart Open API key:

* `pip install requests`
* Register and grab your API key in the [Walmart Open API Developer portal](https://developer.walmartlabs.com/).

##Installation
Installation via `pip` is recommended:
```
pip install wapy
```

You can also install it from source:
```
git clone https://github.com/caroso1222/wapy
cd wapy
python setup.py install
```

##Basic usage
```Python
from wapy.api import Wapy

wapy = Wapy('your-walmart-api-key') # Create an instance of Wapy.

#### PRODUCT LOOKUP ####
product = wapy.product_lookup('21853453') # Perform a product lookup using the item ID.
print (product.name) # Apple EarPods with Remote and Mic MD827LLA
print (product.weight) # 1.0
print (product.customer_rating) # 4.445
print (product.medium_image) # https://i5.walmartimages.com/asr/6cd9c...

#### PRODUCT SEARCH ####
products = wapy.search('xbox')
for product in products:
    print (product.name)
```

##Contribution

There are still some things to do to make Wapy a super badass Python wrapper for the Walmart Open API:
* Return reviews statistics
* Return all the Special Feeds. Already implemented: Bestsellers, Clearance, Special Buy. Still not implemented:
  * preOrder
  * rollback
* Get the categories taxonomy. *Not sure whether or not this would be useful at all*
* Support for Data Feed API. *Similar results can be achieved through the search method by passing a categoryId as an argument.*
* Unit testing
* Improve documentation

Please open up an issue and let me know what you're working on. Feel free to make a PR.

##Credits
- Wapy was inspired by [this awesome Python wrapper for the Amazon product API](https://github.com/yoavaviram/python-amazon-simple-product-api). I took from it some of the code structure, several design parameters and best practices.
- Most of the source code documentation is based on the original [Walmart API specification](https://developer.walmartlabs.com/docs).

##License
Wapy is under [MIT licence](https://opensource.org/licenses/mit-license.php)
