import requests
import json
try:
    # Python 2.6-2.7
    from HTMLParser import HTMLParser
except ImportError:
    # Python 3
    from html.parser import HTMLParser

h = HTMLParser()
API_BASE_URL='http://api.walmartlabs.com/v1/'

class WalmartException(Exception):
    """Base Class for Walmart Api Exceptions.
    """

class NoLinkShareIDException(WalmartException):
    """Exception thrown if no LinkShare ID was specified when creating the Walmart API instance
    """
    pass

class InvalidParameterException(WalmartException):
    """Exception thrown if an invalid parameter is passed to a function
    """
    pass

class InvalidRequestException(WalmartException):
    """Exception thrown if an invalid request response is return by Walmart
    """

    def __init__(self, status_code, **kwargs):
        error_message = 'Error'
        if status_code == 400:
            error_message = 'Bad Request'
            if 'detail' in kwargs:
                error_message = error_message + ' - ' + kwargs['detail']
        elif status_code == 403:
            error_message = 'Forbidden'
        elif status_code == 404:
            error_message = 'Wrong endpoint'
        elif status_code == 414:
            error_message = 'Request URI too long'
        elif status_code == 500:
            error_message = 'Internal Server Error'
        elif status_code == 502:
            error_message = 'Bad Gateway'
        elif status_code == 503:
            error_message = 'Service Unavailable/ API maintenance'
        elif status_code == 504:
            error_message = 'Gateway Timeout'
        message = '[Request failed] Walmart server answered with the following error: {0:s}. Status code: {1:d}'.format(error_message, status_code)
        super(self.__class__, self).__init__(message)
    pass

class Wapy:
    """Models the main Walmart API proxy class
    """

    def __init__(self, api_key, **kwargs):
        """Initialize a Walmart API Proxy

        :param api_key:
            A string representing the Walmart Open API key. Can be found in 'My Account' when signing in your Walmartlabs account.

        - Named params passed in kwargs:
            :param LinkShareID [Optional]
                Your own LinkShare ID. It can be found in any link you generate from the LinkShare platform after the 'id=' parameter. It is an 11 digit alphanumeric string.
        """
        self.params = {'apiKey':api_key,'format':'json'}
        self.LSNID = kwargs.get('LinkShareID')

    def product_lookup(self, item_id, **kwargs):
        """Walmart product lookup

        :param item_id:
            A string representing the product item id

        - Named params passed in kwargs:
            :param richAttributes [Optional]
                A boolean to specify whether you want to get your reponse with rich attributes or not. It's True by default.

        :return:
            An instance of :class: `~.WalmartProduct

        """
        url = API_BASE_URL + 'items/'+item_id
        data = self._send_request(url, **kwargs).json()
        return WalmartProduct(data, self.LSNID)

    def search(self, query, **kwargs):
        """Search allows text search on the Walmart.com catalogue and returns matching items available for sale online.

        This implementation doesn't take into account the start parameter from the actual Walmart specification.
        Instead, we've abstracted the same concept to a paginated approach.
        You can specify which 'page' of results you get, according to the numItems you expect from every page.

        :param query:
            Search text - whitespace separated sequence of keywords to search for

        - Named params passed in kwargs:
            :param numItems [Optional]
                Number of matching items to be returned, max value 25. Default is 10.

            :param page [Optional]
                Number of page retrieved. Each page contains [numItems] elements. If no numItems is specified, a default page contains 10 elements.

            :param categoryId [Optional]
                Category id of the category for search within a category. This should match the id field from Taxonomy API

            :param sort [Optional]
                Sorting criteria, allowed sort types are [relevance, price, title, bestseller, customerRating, new]. Default sort is by relevance.

            :param order [Optional]
                Sort ordering criteria, allowed values are [asc, desc]. This parameter is needed only for the sort types [price, title, customerRating].

            :param responseGroup [Optional]
                Specifies the item fields returned in the response, allowed response groups are [base, full]. Default value is base.

            :param facet [Optional]
                Boolean flag to enable facets. Default value is off. Set this to on to enable facets.

            :param facet.filter [Optional]
                Filter on the facet attribute values.
                This parameter can be set to <facet-name>:<facet-value> (without the angles).
                Here facet-name and facet-value can be any valid facet picked from the search API response when facets are on.

            :param facet.range [Optional]
                Range filter for facets which take range values, like price. See usage above in the examples.

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        url = API_BASE_URL + 'search'
        kwargs['query'] = query
        if 'page' in kwargs:
            if type(kwargs['page']) != int:
                raise InvalidParameterException('Page should be a numeric value')
            if 'numItems' in kwargs:
                if type(kwargs['numItems']) != int:
                    raise InvalidParameterException('Number of items should be a numeric value')
                if kwargs['numItems']>25:
                    raise InvalidParameterException('Number of items must not exceed 25')
                kwargs['start'] = kwargs['numItems']*(kwargs['page']-1) + 1
            else:
                #if numItems not specified, use 10 as default items per page as Walmart does too
                kwargs['start'] = 10*(kwargs['page']-1) + 1
        kwargs.pop('page', None)
        data = self._send_request(url, **kwargs).json()
        products = []
        for item in data["items"]:
            products.append(WalmartProduct(item, self.LSNID))
        return products


    def product_recommendations(self, item_id):
        """Returns a list of a product's related products.

        A maximum of 10 items are returned, being ordered from most relevant to least relevant for the customer.

        :param item_id:
            The id of the product from which the related products are returned

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        url = API_BASE_URL + 'nbp'
        data = self._send_request(url, itemId=item_id).json()
        products = []
        for item in data:
            products.append(WalmartProduct(item, self.LSNID))
        return products

    def post_browsed_products(self, item_id):
        """Returns a list of recommended products based on their product viewing history.

        A maximum of 10 items are returned, being ordered from most relevant to least relevant for the customer.

        :param item_id:
            The id of the product from which the post browsed products are returned

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        url = API_BASE_URL + 'postbrowse'
        data = self._send_request(url, itemId=item_id).json()
        products = []
        for item in data:
            products.append(WalmartProduct(item, self.LSNID))
        return products

    def product_reviews(self, item_id):
        """Return the list of item reviews written by Walmart users.

        :param item_id:
            The id of the product which reviews are returned from

        :return:
            A list of :class:`~.WalmartProductReview`.
        """
        url = API_BASE_URL + 'reviews/' + item_id
        data = self._send_request(url).json()
        reviews = []
        for item in data['reviews']:
            reviews.append(WalmartProductReview(item))
        return reviews

    def trending_products(self):
        """Return a list of items according to what is bestselling on Walmart.com right now.

        The items are curated on the basis of user browse activity and sales activity, and updated multiple times a day.

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        url = API_BASE_URL + 'trends'
        data = self._send_request(url).json()
        products = []
        for item in data['items']:
            products.append(WalmartProduct(item, self.LSNID))
        return products

    def bestseller_products(self, category):
        """Return a list of bestselling items in their respective categories on Walmart.com

        This method is part of the Special Feeds section of the Walmart API.

        :param category:
            The number id of the category from which the products are retrieved.

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        url = API_BASE_URL + 'feeds/bestsellers'
        return self._send_special_feed_request(url, category)

    def clearance_products(self, category):
        """Return a list of all items on clearance from a category

        This method is part of the Special Feeds section of the Walmart API.

        :param category:
            The number id of the category from which the products are retrieved.

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        url = API_BASE_URL + 'feeds/clearance'
        return self._send_special_feed_request(url, category)

    def special_buy_products(self, category):
        """Return a list of all items on Special Buy on Walmart.com, which means there is a special offer on them

        This method is part of the Special Feeds section of the Walmart API.

        :param category:
            The number id of the category from which the products are retrieved.

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        url = API_BASE_URL + 'feeds/specialbuy'
        return self._send_special_feed_request(url, category)

    def _send_special_feed_request(self, url, category):
        """Send a request to the Special Feeds endpoint and returns the desired list of products

        :param category:
            The number id of the category from which the products are retrieved.

        :return:
            A list of :class:`~.WalmartProduct`.
        """
        if type(category) != int:
            raise InvalidParameterException('Category must be numeric. See Walmart Taxonomy API for more information.')
        data = self._send_request(url, categoryId=category).json()
        products = []
        for item in data['items']:
            products.append(WalmartProduct(item, self.LSNID))
        return products

    def _send_request(self, url, **kwargs):
        """Sends a request to the Walmart API and return the HTTP response.

        Important remarks:
            - If the response's status code is differente than 200 or 201, raise an InvalidRequestException with the appripiate code
            - Format is json by default and cannot be changed through kwargs
            - Send richAttributes='true' by default. Can be set to 'false' through kwargs

        :param url:
            The endpoint url to make the request

        - Named params passed in kwargs can be any of the optional GET arguments specified in the Walmart specification
        """
        #Avoid format to be changed, always go for json
        kwargs.pop('format', None)
        request_params = self.params
        for key, value in kwargs.items():
            request_params[key] = value

        #Convert from native boolean python type to string 'true' or 'false'. This allows to set richAttributes with python boolean types
        if 'richAttributes' in request_params and type(request_params['richAttributes'])==bool:
            if request_params['richAttributes']:
                request_params['richAttributes']='true'
            else:
                request_params['richAttributes']='false'
        else:
            #Even if not specified in arguments, send request with richAttributes='true' by default
            request_params['richAttributes']='true'

        r = requests.get(url, params=request_params)
        if r.status_code == 200 or r.status_code == 201:
            return r
        else:
            if r.status_code == 400:
                #Send exception detail when it is a 400 error
                raise InvalidRequestException(r.status_code, detail=r.json()['errors'][0]['message'])
            else:
                raise InvalidRequestException(r.status_code)


class WalmartProduct:
    """Models a Walmart Product as an object
    """

    def __init__(self, payload, LSNID):
        self.LSNID = LSNID
        self.response_handler = ResponseHandler(payload)

    @property
    def item_id(self):
        """Item id: A positive integer that uniquely identifies an item

        :return:
            Item id (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('itemId')

    @property
    def parent_item_id(self):
        """Parent Item id: Item Id of the base version for this item. This is present only if item is a variant of the base version, such as a different color or size.

        :return:
            Parent Item id (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('parentItemId')

    @property
    def name(self):
        """Item name

        :return:
            Standard name of the item (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute_text('name')

    @property
    def msrp(self):
        """Manufacturer suggested retail price

        :return:
            Manufacturer suggested retail price (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('msrp')

    @property
    def sale_price(self):
        """Sale price

        :return:
            Selling price for the item in USD (float). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute_float('salePrice')

    @property
    def upc(self):
        """Unique Product Code

        :return:
            Unique Product Code (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('upc')

    @property
    def category_path(self):
        """Product Category path: Breadcrumb for the item. This string describes the category level hierarchy that the item falls under.

        :return:
            Product Category path (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('categoryPath')

    @property
    def category_node(self):
        """Product Category node: Category id for the category of this item. This value can be passed to APIs to pull this item's category level information.

        :return:
            Product Category path (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('categoryNode')

    @property
    def short_description(self):
        """Short description: Short description for the item

        :return:
            Short description (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute_text('shortDescription')

    @property
    def long_description(self):
        """Long description: Long description for the item.

        :return:
            Long description (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute_text('shortDescription')

    @property
    def brand_name(self):
        """Brand name: Item's brand

        :return:
            Brand name (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('brandName')

    @property
    def thumbnail_image(self):
        """Thumbnail image: Small size image for the item in jpeg format with dimensions 100 x 100 pixels

        :return:
            URL of the thumbnail image (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('thumbnailImage')

    @property
    def medium_image(self):
        """Medium image: Medium size image for the item in jpeg format with dimensions 180 x 180 pixels

        :return:
            URL of the medium sized image (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('mediumImage')

    @property
    def large_image(self):
        """Large image: Large size image for the item in jpeg format with dimensions 450 x 450 pixels

        :return:
            URL of the large sized image (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('largeImage')

    @property
    def images(self):
        """Large image entities: All large images for this item

        :return:
            A list with all the large size images URLs.
            Primary image is always returned in the first position of the list
        """
        return self.get_images_by_size('large')

    @property
    def product_tracking_url(self):
        """Product tracking url: Deep linked URL that directly links to the product page of this item on walmart.com.
        This link uniquely identifies the affiliate sending this request via a linkshare tracking id |LSNID|.
        The LSNID parameter needs to be replaced with your linkshare tracking id, and is used by us to correctly attribute the sales from your channel on walmart.com.
        Actual commission numbers will be made available through your linkshare account.

        :return:
            Deep link URL (string). Returns None if attribute is not found in the response.
        """
        if self.LSNID is None:
            raise NoLinkShareIDException('No LinkShare ID specified. When retrieving the product tracking url, you must set LinkShareID = #YOUR_ID# when creating an instance of the API')
        else:
            return self.response_handler._safe_get_attribute('productTrackingUrl').replace('|LSNID|',self.LSNID)

    @property
    def size(self):
        """Size attribute for the item

        :return:
            Size attribute for the item (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('size')

    @property
    def color(self):
        """Color attribute for the item

        :return:
            Color attribute for the item (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('color')

    @property
    def model_number(self):
        """Model number: Model number attribute for the item

        :return:
            Model number. (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('modelNumber')

    @property
    def product_url(self):
        """Product url: Walmart.com url for the item

        :return:
            Product url. (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('productUrl')

    @property
    def available_online(self):
        """Available online: Whether the item is currently available for sale on Walmart.com

        :return:
            Available online. (boolean). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('availableOnline')

    @property
    def stock(self):
        """Stock: Indicative quantity of the item available online.

        Possible values are [Available, Limited Supply, Last few items, Not available].
        Limited supply: can go out of stock in the near future, so needs to be refreshed for availability more frequently.
        Last few items: can go out of stock very quickly, so could be avoided in case you only need to show available items to your users.

        :return:
            Stock. (string). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute('stock')

    @property
    def customer_rating(self):
        """Customer rating: Average customer rating out of 5

        :return:
            Customer rating. (float). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute_float('customerRating')

    @property
    def num_reviews(self):
        """Number of customer reviews available on this item on Walmart.com

        :return:
            Number of reviews. (int). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute_int('numReviews')

    @property
    def weight(self):
        """Weight: Indicates the weight of the item

        :return:
            Weight (float). Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute_float('weight')

    @property
    def length(self):
        """Length: Indicates the length of the item. First dimension returned by attribute dimensions
                   e.g. dimensions: "2.0 x 3.0 x 4.0" would return 2.0 as length

        :return:
            Length (float). Returns None if attribute is not found in the response.
        """
        dimensions = self.response_handler._safe_get_attribute('dimensions')
        if dimensions is not None:
            return float(dimensions.split('x')[0])
        return None

    @property
    def width(self):
        """Width: Indicates the width of the item. Second dimension returned by attribute dimensions
                  e.g. dimensions: "2.0 x 3.0 x 4.0" would return 3.0 as width
        :return:
            Width (float). Returns None if attribute is not found in the response.
        """
        dimensions = self.response_handler._safe_get_attribute('dimensions')
        if dimensions is not None:
            return float(dimensions.split('x')[1])
        return None

    @property
    def height(self):
        """Height: Indicates the height of the item. Third dimension returned by attribute dimensions
                  e.g. dimensions: "2.0 x 3.0 x 4.0" would return 4.0 as height
        :return:
            Height (float). Returns None if attribute is not found in the response.
        """
        dimensions = self.response_handler._safe_get_attribute('dimensions')
        if dimensions is not None:
            return float(dimensions.split('x')[2])
        return None

    def get_attribute(self, name):
        """ Returns any of the product attributes from the Full Response group.

        :param name:
            Name of the product attribute. See docs to see the allowed params

        :return:
            The value of the product attribute. (String). User must be aware that he must parse the response to float or integer himself.
            Returns None if attribute is not found in the response.
        """
        return self.response_handler._safe_get_attribute(name)

    def get_images_by_size(self, size):
        """Image entities: All images for this item

        :param size:
            Indicates the size of the returned images: possible options are: 'thumbnail', 'medium', 'large'

        :return:
            A list with all the images URLs.
            Primary image is always returned in the first position of the list
        """
        if size != 'thumbnail' and size != 'medium' and size != 'large':
            raise InvalidParameterException("The image size should be 'thumbnail', 'medium' or 'large'")
        images = []
        primary_image = None
        imageEntities = self.response_handler._safe_get_attribute('imageEntities')
        if imageEntities:
            for image in imageEntities:
                if image['entityType'] != 'PRIMARY':
                    images.append(image[size+'Image'])
                else:
                    primary_image = image[size+'Image']
            if primary_image:
                images.insert(0, primary_image)
            return images
        else:
            return None

class WalmartProductReview:
    """Models a Walmart Product review as an object
    """

    def __init__(self, payload):
        self.response_handler = ResponseHandler(payload)

    @property
    def reviewer(self):
        """Product reviewer

        :return:
            Name/alias of the reviewer (string)
        """
        return self.response_handler._safe_get_attribute('reviewer')

    @property
    def review(self):
        """Product review

        :return:
            The complete product review (string)
        """
        return self.response_handler._safe_get_attribute_text('reviewText')

    @property
    def date(self):
        """Product review date

        :return:
            The product review date (string)
        """
        return self.response_handler._safe_get_attribute_text('submissionTime')

    @property
    def title(self):
        """Product review title

        :return:
            Product review title (string)
        """
        return self.response_handler._safe_get_attribute_text('title')

    @property
    def up_votes(self):
        """Product review up votes

        :return:
            Number of up votes for this review (int)
        """
        return self.response_handler._safe_get_attribute_int('upVotes')

    @property
    def down_votes(self):
        """Product review down votes

        :return:
            Number of down votes for this review (int)
        """
        return self.response_handler._safe_get_attribute_int('downVotes')

    @property
    def rating(self):
        """Overall review rating

        :return:
            Overall rating given by the reviewer (int)
        """
        if 'overallRating' in self.response_handler.payload and 'rating' in self.response_handler.payload['overallRating']:
            return int(self.response_handler.payload['overallRating']['rating'])
        else:
            return None

class ResponseHandler:
    """Gets a json payload and exposes some attributes to safely get attributes from it
    """

    def __init__(self, payload):
        self.payload = payload

    def _safe_get_attribute(self, attr):
        """ Safe get element attribute. Fails silently if attribute not found.

        :param attr:
            The name of attribute

        :return:
            The value of the attribute in the response. Returns None if attribute is not found in the response.
        """
        if attr in self.payload:
            return self.payload[attr]
        else:
            return None

    def _safe_get_attribute_text(self, attr):
        """ Safe get element attribute with unescaped html entities. Fails silently if attribute not found.

        :param attr:
            The name of attribute

        :return:
            The value of the attribute in the response. (string). Returns None if attribute is not found in the response.
            Some attributes come with escaped html entities. This method will unescape them.
        """
        if attr in self.payload:
            # some strings contains escaped html formatting tags.
            return h.unescape(self.payload[attr])
        else:
            return None

    def _safe_get_attribute_float(self, attr):
        """ Safe get element attribute parsed to float. Fails silently if attribute not found.

        :param attr:
            The name of attribute

        :return:
            The value of the attribute parsed to float. (float). Returns None if attribute is not found in the response.
        """
        if attr in self.payload:
            return float(self.payload[attr])
        else:
            return None

    def _safe_get_attribute_int(self, attr):
        """ Safe get element attribute parsed to int. Fails silently if attribute not found.

        :param attr:
            The name of attribute

        :return:
            The value of the attribute parsed to int. (int). Returns None if attribute is not found in the response.
        """
        if attr in self.payload:
            return int(self.payload[attr])
        else:
            return None
