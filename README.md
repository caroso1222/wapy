# Wapy      
Wapy is a fully featured Python wrapper for the Walmart Open API.

## Features
* Easy to use, object oriented interface to the Walmart Open API. (*Products and Reviews are retrieved as objects*)
* Ready to use, parsed attributes. *e.g. prices as `float`, no strings with escaped html entities, numbers as `int`.*
* Full support for Walmart Search API, Product Recommendation API, Post Browsed Products API, Trending API and more.
* Get all responses with `richAttributes='true'` by default. *This lets you get weight and dimensions right off the shelf.*
* Proper error handling according to original Walmart API documentation
* Helper functions such as `bestseller_products()` and more from the Special Feeds section.
* Silently fails when attribute not found in response
* Fully documented source code
* Support for Python 2.7, 3.2, 3.3, 3.4 and 3.5

## Requirements
Before using Wapy, you want to make sure you have `requests` installed and a Walmart Open API key:

* `pip install requests`
* Register and grab your API key in the [Walmart Open API Developer portal](https://developer.walmartlabs.com/).

## Installation
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

## Basic usage
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

#### PRODUCT REVIEWS ####
reviews = wapy.product_reviews('21853453')
for review in reviews:
    print (product.reviewer)
```

This example barely shows the power of Wapy. Read the API documentation to discover all you can achieve with this library.

## API documentation

### `class Wapy`
This class models the main Walmart API proxy class and offers services such as product lookup, product search, trending products retrieval, and much more.

### Methods
#### `__init__([api_key], **kwargs)`
Initialize a Walmart API Proxy.

##### Params#####
* **`api_key`** A string representing the Walmart Open API key. Can be found in 'My Account' when signing in your Walmartlabs account.
* Named **optional** params passed in kwargs:
  * **`LinkShareID`** Your own LinkShare ID. It can be found in any link you generate from the LinkShare platform after the 'id=' parameter. It is an 11 digit alphanumeric string.

#### `product_lookup([item_id], **kwargs)`
Walmart product lookup.

##### Params #####
* **`item_id`** A string representing the product item id.
* Named **optional** params passed in kwargs:
  * **`richAttributes`** A boolean to specify whether you want to get your reponse with rich attributes or not. It's True by default.

##### Return #####
An instance of `WalmartProduct`. <[*[WalmartProduct](#class-walmartproduct)*]>

#### `search([query], **kwargs)`

Search allows text search on the Walmart.com catalogue and returns matching items available for sale online.

This implementation doesn't take into account the start parameter from the actual Walmart specification.
Instead, I've abstracted the same concept to a paginated approach.
You can specify which 'page' of results you get, according to the numItems you expect from every page.

##### Params #####
* **`query`** Search text - whitespace separated sequence of keywords to search for
* Unnamed params passed in kwargs:
  * **`numItems`** Number of matching items to be returned, max value 25. Default is 10.
  * **`page`** Number of page retrieved. Each page contains [numItems] elements. If no numItems is specified, a default page contains 10 elements.
  * **`categoryId`** Category id of the category for search within a category. This should match the id field from Taxonomy API
  * **`sort`** Sorting criteria, allowed sort types are [relevance, price, title, bestseller, customerRating, new]. Default sort is by relevance.
  * **`order`** Sort ordering criteria, allowed values are [asc, desc]. This parameter is needed only for the sort types [price, title, customerRating].
  * **`responseGroup`** Specifies the item fields returned in the response, allowed response groups are [base, full]. Default value is base.
  * **`facet`** Boolean flag to enable facets. Default value is off. Set this to on to enable facets.
  * **`facet.filter`** Filter on the facet attribute values. This parameter can be set to <facet-name>:<facet-value> (without the angles). Here facet-name and facet-value can be any valid facet picked from the search API response when facets are on.
  * **`facet.range`** Range filter for facets which take range values, like price. See usage above in the examples.

##### Return #####
A list of `WalmartProduct` instances. <[*[WalmartProduct](#class-walmartproduct)*]>

####`product_recommendations([item_id])`
Returns a list of a product's related products. A maximum of 10 items are returned, being ordered from most relevant to least relevant for the customer.

##### Params #####
* **`item_id`** The id of the product from which the related products are returned

##### Return #####
A list of `WalmartProduct` instances. <[*[WalmartProduct](#class-walmartproduct)*]>

#### `post_browsed_products([item_id])`

Returns a list of recommended products based on their product viewing history. A maximum of 10 items are returned, being ordered from most relevant to least relevant for the customer.

##### Params #####
* **`item_id`** The id of the product from which the post browsed products are returned

##### Return #####
A list of `WalmartProduct` instances. <[*[WalmartProduct](#class-walmartproduct)*]>

#### `product_reviews([item_id])`
Returns the list of reviews written by Walmart users for a specific item.

##### Params #####
* **`item_id`** The id of the product which reviews are returned from

##### Return #####
A list of `WalmartProductReview` instances. <[*[WalmartProductReview](#class-walmartproductreview)*]>

#### `trending_products()`

Returns a list of items according to what is bestselling on Walmart.com right now. The items are curated on the basis of user browse activity and sales activity, and updated multiple times a day.

##### Return #####
A list of `WalmartProduct` instances. <[*[WalmartProduct](#class-walmartproduct)*]>

#### `bestseller_products([category])`

Return a list of bestselling items in their respective categories on Walmart.com. This method is part of the Special Feeds section of the Walmart API.

##### Params #####
* **`category`** The number id of the category from which the products are retrieved.

##### Return #####
A list of `WalmartProduct` instances. <[*[WalmartProduct](#class-walmartproduct)*]>

#### `clearance_products([category])`

Return a list of all items on clearance from a category. This method is part of the Special Feeds section of the Walmart API.

##### Params #####
* **`category`** The number id of the category from which the products are retrieved.

##### Return #####
A list of `WalmartProduct` instances. <[*[WalmartProduct](#class-walmartproduct)*]>

#### `special_buy_products([category])`

Return a list of all items on Special Buy on Walmart.com, which means there is a special offer on them. This method is part of the Special Feeds section of the Walmart API.

##### Params #####
* **`category`** The number id of the category from which the products are retrieved.

##### Return #####
A list of `WalmartProduct` instances. <[*[WalmartProduct](#class-walmartproduct)*]>

---

### `class WalmartProduct`
This class models a Walmart Product as an object. A `WalmartProduct` instance will be returned when performing a `product_lookup` from your Wapy instance.
### Methods
#### `get_attribute([name])`
Returns any of the product attributes from the Full Response group. When using this method to get attribute values, you must parse the response to float or integer whenever needed. **I don't recommend accessing attributes using this method**. Direct attribute access is preferred. See **Atributes** section below.

##### Params #####
* **`name`** Product attribute's name. Check out the **Atributes** section below to see allowed names.

##### Return #####

The product attribute value. <*string*>

#### `get_images_by_size([size])`
A list with all the images URLs. Primary image is always returned in the first position of the list.

##### Params #####
* **`size`** Size of the desired images: possible options are: 'thumbnail', 'medium', 'large'.

##### Return #####

List with all the images URLs. <*[string]*>

### Attributes
All properties return `None` if not found in the Walmart API response.
#### `item_id`
A positive integer that uniquely identifies an item. <*string*>
#### `parent_item_id`
Item Id of the base version for this item. This is present only if item is a variant of the base version, such as a different color or size. <*string*>
#### `name`
Standard name of the item. <*string*>
#### `msrp`
Manufacturer suggested retail price. <*string*>
#### `sale_price`
Selling price for the item in USD. <*float*>
#### `upc`
Unique Product Code. <*string*>
#### `category_path`
Product Category path: Breadcrumb for the item. This string describes the category level hierarchy that the item falls under. <*string*>
#### `category_node`
Category id for the category of this item. This value can be passed to APIs to pull this item's category level information. <*string*>
#### `short_description`
Short description for the item. <*string*>
#### `long_description`
Long description for the item. <*string*>
#### `brand_name`
Item's brand name. <*string*>
#### `thumbnail_image`
URL for the small sized image. This is a jpeg image with dimensions 100 x 100 pixels. <*string*>
#### `medium_image`
URL for the medium sized image. This is a jpeg image with dimensions 180 x 180 pixels. <*string*>
#### `large_image`
URL for the large sized image. This is a jpeg image with dimensions 450 x 450 pixels. <*string*>
#### `images`
A list with all the large size images URLs. Primary image is always returned in the first position of the list. <[*string*]>
#### `product_tracking_url`
Deep linked URL that directly links to the product page of this item on walmart.com.
This link uniquely identifies the affiliate sending this request via a linkshare tracking id |LSNID|.
The LSNID parameter needs to be replaced with your linkshare tracking id, and is used by us to correctly attribute the sales from your channel on walmart.com.
Actual commission numbers will be made available through your linkshare account. <*string*>

**Note:** If you created a Wapy instance without explicitly setting `LinkShareID`, you'll get a `NoLinkShareIDException` exception when trying to access this property.
#### `size`
Size attribute for the item. <*string*>
#### `color`
Color attribute for the item. <*string*>
#### `model_number`
Model number attribute for the item. <*string*>
#### `product_url`
Walmart.com url for the item. <*string*>
#### `available_online`
Whether or not the item is currently available for sale on Walmart.com. <*boolean*>
#### `stock`
Indicative quantity of the item available online. Possible values are [Available, Limited Supply, Last few items, Not available]. <*string*>

Limited supply: can go out of stock in the near future, so needs to be refreshed for availability more frequently.

Last few items: can go out of stock very quickly, so could be avoided in case you only need to show available items to your users.
#### `customer_rating`
Average customer rating out of 5. <*float*>
#### `num_reviews`
Number of customer reviews available on this item on Walmart.com. <*int*>
#### `weight`
Indicates the weight of the item. <*float*>
#### `length`
Indicates the length of the item. First dimension returned by attribute dimensions e.g. dimensions: "2.0 x 3.0 x 4.0" would return 2.0 as length. <*float*>
#### `width`
Indicates the width of the item. Second dimension returned by attribute dimensions e.g. dimensions: "2.0 x 3.0 x 3.0" would return 3.0 as width. <*float*>
#### `height`
Indicates the height of the item. Third dimension returned by attribute dimensions e.g. dimensions: "2.0 x 3.0 x 4.0" would return 4.0 as height. <*float*>
#### `color`
Color attribute for the item. <*string*>

---

### `class WalmartProductReview`
This class models a Walmart Product review as an object. A list containing `WalmartProductReview` instances will be returned when calling the method `product_reviews` from your Wapy instance.
### Attributes
All properties return `None` if not found in the Walmart API response.
#### `reviewer`
Name/alias of the reviewer. <*string*>
#### `review`
The complete product review. <*string*>
####`date`
The product review date. <*string*>
#### `up_votes`
Number of up votes for this review. <*int*>
#### `down_votes`
Number of down votes for this review. <*int*>
#### `rating`
Overall rating given by the reviewer. <*int*>


## Contribution

There are still some things to do to make Wapy a super badass Python wrapper for the Walmart Open API:
* Return reviews statistics
* Return all the Special Feeds. Already implemented: Bestsellers, Clearance, Special Buy. Still not implemented:
  * preOrder
  * rollback
* Get the categories taxonomy. *Not sure whether or not this would be useful at all*
* Support for Data Feed API. *Similar results can be achieved through the search method by passing a categoryId as an argument.*
* Unit testing

Please open up an issue and let me know what you're working on. Feel free to make a PR.

## Credits
- Wapy was inspired by [this awesome Python wrapper for the Amazon product API](https://github.com/yoavaviram/python-amazon-simple-product-api). I took from it some of the code structure, several design parameters and best practices.
- Most of the documentation is based on the original [Walmart API specification](https://developer.walmartlabs.com/docs).

## License
Wapy is under [MIT licence](https://opensource.org/licenses/mit-license.php)
