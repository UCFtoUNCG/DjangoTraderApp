from django.db import models


class Customers(models.Model):

    # region Customer Fields from Database.
    customer_id = models.CharField(primary_key=True, max_length=5)
    company_name = models.CharField(max_length=40)
    contact_name = models.CharField(max_length=30, blank=True, null=True)
    contact_title = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    region = models.CharField(max_length=15, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    password = models.CharField(
        db_column="Password", max_length=64, blank=True, null=True
    )
    # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "customers"

    # endregion

    # Added Model Instance Methods
    def __str__(self):
        """
        String representation of the Customer object.
        An f-string is a string formatting method .
        It allows embedding expressions directly inside strings
        using the f prefix and placing variables or expressions
        inside curly braces {}.

        This __str__ function
        returns the company and contact names using the f-string:
        """
        return f"Company: {self.company_name} [Contact: {self.contact_name}]"

    def get_full_address(self):
        """
        Returns the full address of the customer by concatenating
        the address, city, region, postal code, and country.
        """
        return f"{self.address}, {self.city}, {self.region}, {self.postal_code}, {self.country}"

    # region Added in version 1.1
    def get_order_count(self):
        """
        Returns the number of orders associated with this customer.
        Uses the related_name 'orders' defined in the Orders model.
        If no orders exist, it returns 0.
        """
        return self.orders.count()

    def get_orders(self):
        """
        Returns a queryset of all orders associated with this customer.
        Uses the related_name 'orders' defined in the Orders model.
        The Orders are ordered by order_date in descending order - most recent first.
        """
        return self.orders.all().order_by("-order_date")

    def get_ordered_products(self):
        """
        Returns a queryset of all products ordered by this customer.
        Since we're using property-based relationships for OrderDetails,
        we need to manually traverse the relationships.
        """
        # Get all orders for this customer
        customer_orders = self.orders.all()

        # Get all order_ids for this customer
        order_ids = list(customer_orders.values_list("order_id", flat=True))

        # Get all OrderDetails for these orders
        order_details = OrderDetails.objects.filter(order_id__in=order_ids)

        # Get all product_ids from these order details
        product_ids = list(order_details.values_list("product_id", flat=True))

        # Return products that were ordered by this customer
        return Products.objects.filter(product_id__in=product_ids).distinct()

    # endregion Added in version 1.1

    # region Class Methods
    """
    Class methods apply to the class as a whole, rather than to individual instances of the class.
    They are defined using the @classmethod decorator and take cls as the first parameter,
    which refers to the class itself.
    """

    @classmethod
    def get_all_countries(cls):
        """
        Returns a list of all unique countries from the customer records.
        All the countries in this list will be from the current records.

        classmethod: A Member method - a method that is bound to the class and not the instance.
        cls: The class itself. The data type is <class 'DjangoTradersApp.models.Customers'>

        """
        countries = (
            cls.objects.values_list("country", flat=True)
            .distinct()
            .order_by("-country")
        )
        return countries

    # endregion Class Methods


# v1.1 Classes Copied and Edited from GeneratedModels.py.


class Employees(models.Model):
    """
    Need the Employees model here as Order uses Employees to denote the employee that placed the order.
    So we MUST have this model appear before orders to avoid error in the definition of Orders below.
    """

    # region Employee Fields from Database.
    employee_id = models.SmallIntegerField(primary_key=True)
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=10)
    title = models.CharField(max_length=30, blank=True, null=True)
    title_of_courtesy = models.CharField(max_length=25, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    region = models.CharField(max_length=15, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    home_phone = models.CharField(max_length=24, blank=True, null=True)
    extension = models.CharField(max_length=4, blank=True, null=True)
    photo = models.BinaryField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    reports_to = models.ForeignKey(
        "self", models.DO_NOTHING, db_column="reports_to", blank=True, null=True
    )
    photo_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "employees"

    # endregion


# v 1.2 added functionality to calculate line total with discount
class OrderDetails(models.Model):
    """
            Edits/Additions:
    Model:
        1. Added a method to calculate the line total with discount.
        2. Removed ForeignKey relationships and replaced with properties to fetch related objects.
        3. Added comments to explain the use of @property decorator.
        4. Removed CompositePrimaryKey as Django does not support it natively.

    Functions:
        1. order: Property to get the related Order object.
        2. product: Property to get the related Product object.
        3. line_total: Property to calculate the line total after applying discount.

    """

    # region OrderDetails Fields from Database.

    # Note: Removed ForeignKey relationships to Orders and Products.
    # Use only the actual database columns that exist and added properties to fetch related objects instead.
    order_id = models.IntegerField(primary_key=True)
    product_id = models.IntegerField()
    unit_price = models.FloatField()
    quantity = models.SmallIntegerField()
    discount = models.FloatField()

    class Meta:
        managed = False
        db_table = "order_details"

    # endregion

    # Add properties to get related objects
    @property
    def order(self):
        """
        The "@property" decorator is used, instead of a method, to allow access to the object.

        By adding the "@property", you can access it like an attribute, without needing to call it like a method.
        By accessing it as an attribute, you can write cleaner and more intuitive code.
        Most importantly, a property behaves like an attribute, but works like a method
        by executing code inside the property/method when accessed.

        Moreover, the property is stored in memory like an attribute,
        while  method is handled as methods that are called from the dictionary of the parent object.

        Bottom line  - we dont need to call it like a method with parentheses - we can just use "order_details_instance.order"
        to get the Order object related to the OrderDetails instance.
        """
        return Orders.objects.get(order_id=self.order_id)

    @property
    def product(self):
        """
        As with the above, this works just like a method, but is accessed like an attribute.
        Used to get the Product object related to this OrderDetails instance.
        """
        return Products.objects.get(product_id=self.product_id)

    @property
    def line_total(self):
        """
        Calculate the line total after applying discount
        Line Total = (Unit Price * Quantity) - Discount
        Returns the line total as a float.
        """
        gross_total = self.unit_price * self.quantity
        discount_total = gross_total * (self.discount / 100)
        return gross_total - discount_total


class Orders(models.Model):
    """
    Edits/Additions:
    1.  Added related_name="orders" in "customer" to create a reverse relationship from Customers to Orders.
    This allows  every Customer to get their orders using customer.orders.all() and order.customer gets the customer for an order.

    2. Added a method get_order_details to fetch all order details for this order.
        This method returns a  List (queryset) of OrderDetails objects related to this order.

    3. Added a method get_order_total to calculate the total amount for this order.
        This method uses the "sum" function to add up all values of line_total  from the related OrderDetails.
        It returns the total as a float.

    4. Added a property "order_total" to provide easier access to the order total in templates.
        This property does not do anything, it simply asks for the value of get_order_total and returns it.
                This way, in templates, we can use {{ order.order_total }} instead of calling a method.
    """

    # region Order Fields from Database.
    order_id = models.SmallIntegerField(primary_key=True)
    customer = models.ForeignKey(
        Customers, models.DO_NOTHING, blank=True, null=True, related_name="orders"
    )
    employee = models.ForeignKey(Employees, models.DO_NOTHING, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    required_date = models.DateField(blank=True, null=True)
    shipped_date = models.DateField(blank=True, null=True)
    ship_via = models.ForeignKey(
        "Shippers", models.DO_NOTHING, db_column="ship_via", blank=True, null=True
    )
    freight = models.FloatField(blank=True, null=True)
    ship_name = models.CharField(max_length=40, blank=True, null=True)
    ship_address = models.CharField(max_length=60, blank=True, null=True)
    ship_city = models.CharField(max_length=15, blank=True, null=True)
    ship_region = models.CharField(max_length=15, blank=True, null=True)
    ship_postal_code = models.CharField(max_length=10, blank=True, null=True)
    ship_country = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "orders"

    # endregion

    # Added Methods
    def get_order_details(self):
        """
        Get all order details for this order.
        Returns a list of OrderDetails objects.
        """
        return OrderDetails.objects.filter(order_id=self.order_id)

    def get_order_total(self):
        """
        Calculate the total amount for this order by summing all line_total values
        from the related OrderDetails.
        Returns the total as a float.
        """
        order_details = self.get_order_details()
        total = sum(detail.line_total for detail in order_details)
        return total

    @property
    def order_total(self):
        """
        Property version of get_order_total for easier template access.
        """
        return self.get_order_total()


class Categories(models.Model):
    category_id = models.SmallIntegerField(primary_key=True)
    category_name = models.CharField(max_length=15)
    description = models.TextField(blank=True, null=True)
    picture = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "categories"


class Products(models.Model):
    product_id = models.SmallIntegerField(primary_key=True)
    product_name = models.CharField(max_length=40)
    supplier = models.ForeignKey("Suppliers", models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(Categories, models.DO_NOTHING, blank=True, null=True)
    quantity_per_unit = models.CharField(max_length=20, blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)
    units_in_stock = models.SmallIntegerField(blank=True, null=True)
    units_on_order = models.SmallIntegerField(blank=True, null=True)
    reorder_level = models.SmallIntegerField(blank=True, null=True)
    discontinued = models.IntegerField()

    class Meta:
        managed = False
        db_table = "products"


class Region(models.Model):
    region_id = models.SmallIntegerField(primary_key=True)
    region_description = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = "region"


class Shippers(models.Model):
    shipper_id = models.SmallIntegerField(primary_key=True)
    company_name = models.CharField(max_length=40)
    phone = models.CharField(max_length=24, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "shippers"


class Suppliers(models.Model):
    supplier_id = models.SmallIntegerField(primary_key=True)
    company_name = models.CharField(max_length=40)
    contact_name = models.CharField(max_length=30, blank=True, null=True)
    contact_title = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    region = models.CharField(max_length=15, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    homepage = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "suppliers"
