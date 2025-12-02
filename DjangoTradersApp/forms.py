from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Customers, Products, Employees, Shippers, Orders, OrderDetails, Categories, Suppliers


class CustomerSelectionForm(forms.Form):
    """Form for selecting a customer when starting an order."""
    customer = forms.ModelChoiceField(
        queryset=Customers.objects.all(),
        label="Select Customer",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select a Customer --"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].label_from_instance = lambda obj: f"{obj.company_name} ({obj.customer_id})"


class ProductSelectionForm(forms.Form):
    """Form for selecting a product with quantity and discount."""
    product = forms.ModelChoiceField(
        queryset=Products.objects.filter(discontinued=0),
        label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select a Product --"
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    discount = forms.FloatField(
        min_value=0,
        max_value=100,
        initial=0,
        label="Discount (%)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '0.1'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda obj: f"{obj.product_name} - ${obj.unit_price:.2f}"

    def clean_product(self):
        product = self.cleaned_data.get('product')
        if product and product.discontinued == 1:
            raise ValidationError("This product has been discontinued and cannot be ordered.")
        return product


class OrderDetailsForm(forms.Form):
    """Form for entering order details like employee, required date, and shipper."""
    employee = forms.ModelChoiceField(
        queryset=Employees.objects.all(),
        label="Assign Employee (for commission)",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select an Employee --"
    )
    required_date = forms.DateField(
        label="Required Date",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=lambda: date.today() + timedelta(days=7)
    )
    shipper = forms.ModelChoiceField(
        queryset=Shippers.objects.all(),
        label="Shipper",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select a Shipper --"
    )
    ship_name = forms.CharField(
        max_length=40,
        label="Ship To Name",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ship_address = forms.CharField(
        max_length=60,
        label="Ship Address",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ship_city = forms.CharField(
        max_length=15,
        label="Ship City",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ship_region = forms.CharField(
        max_length=15,
        label="Ship Region",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ship_postal_code = forms.CharField(
        max_length=10,
        label="Ship Postal Code",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ship_country = forms.CharField(
        max_length=15,
        label="Ship Country",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, customer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields['shipper'].label_from_instance = lambda obj: obj.company_name
        
        # Pre-fill shipping info from customer if provided
        if customer:
            self.fields['ship_name'].initial = customer.company_name
            self.fields['ship_address'].initial = customer.address
            self.fields['ship_city'].initial = customer.city
            self.fields['ship_region'].initial = customer.region
            self.fields['ship_postal_code'].initial = customer.postal_code
            self.fields['ship_country'].initial = customer.country

    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        if required_date and required_date <= date.today():
            raise ValidationError("Required date must be in the future.")
        return required_date


class ProductForm(forms.ModelForm):
    """Form for creating and updating products."""

    class Meta:
        model = Products
        fields = [
            'product_id',
            'product_name',
            'supplier',
            'category',
            'quantity_per_unit',
            'unit_price',
            'units_in_stock',
            'units_on_order',
            'reorder_level',
            'discontinued',
        ]
        widgets = {
            'product_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity_per_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'units_in_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'units_on_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'discontinued': forms.Select(attrs={'class': 'form-control'}, choices=[(0, 'No'), (1, 'Yes')]),
        }
        labels = {
            'product_id': 'Product ID',
            'product_name': 'Product Name',
            'supplier': 'Supplier',
            'category': 'Category',
            'quantity_per_unit': 'Quantity Per Unit',
            'unit_price': 'Unit Price ($)',
            'units_in_stock': 'Units In Stock',
            'units_on_order': 'Units On Order',
            'reorder_level': 'Reorder Level',
            'discontinued': 'Discontinued',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up supplier label
        self.fields['supplier'].label_from_instance = lambda obj: obj.company_name
        self.fields['supplier'].empty_label = "-- Select a Supplier --"
        # Set up category label
        self.fields['category'].label_from_instance = lambda obj: obj.category_name
        self.fields['category'].empty_label = "-- Select a Category --"

    def clean_product_id(self):
        """Validate product_id is positive."""
        product_id = self.cleaned_data.get('product_id')
        if product_id is not None and product_id <= 0:
            raise ValidationError("Product ID must be a positive integer.")
        # Check for unique product_id only on create (no instance or new instance)
        if not self.instance.pk:
            if Products.objects.filter(product_id=product_id).exists():
                raise ValidationError("A product with this ID already exists.")
        return product_id

    def clean_product_name(self):
        """Validate product_name is not empty and within length constraints."""
        product_name = self.cleaned_data.get('product_name')
        if not product_name or not product_name.strip():
            raise ValidationError("Product name is required.")
        if len(product_name) > 40:
            raise ValidationError("Product name must be 40 characters or less.")
        return product_name.strip()

    def clean_unit_price(self):
        """Validate unit_price is non-negative."""
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is not None and unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        return unit_price

    def clean_units_in_stock(self):
        """Validate units_in_stock is non-negative."""
        units_in_stock = self.cleaned_data.get('units_in_stock')
        if units_in_stock is not None and units_in_stock < 0:
            raise ValidationError("Units in stock cannot be negative.")
        return units_in_stock

    def clean_units_on_order(self):
        """Validate units_on_order is non-negative."""
        units_on_order = self.cleaned_data.get('units_on_order')
        if units_on_order is not None and units_on_order < 0:
            raise ValidationError("Units on order cannot be negative.")
        return units_on_order

    def clean_reorder_level(self):
        """Validate reorder_level is non-negative."""
        reorder_level = self.cleaned_data.get('reorder_level')
        if reorder_level is not None and reorder_level < 0:
            raise ValidationError("Reorder level cannot be negative.")
        return reorder_level

    def clean_quantity_per_unit(self):
        """Validate quantity_per_unit is within length constraints."""
        quantity_per_unit = self.cleaned_data.get('quantity_per_unit')
        if quantity_per_unit and len(quantity_per_unit) > 20:
            raise ValidationError("Quantity per unit must be 20 characters or less.")
        return quantity_per_unit

    def clean_discontinued(self):
        """Validate discontinued is 0 or 1."""
        discontinued = self.cleaned_data.get('discontinued')
        if discontinued not in [0, 1]:
            raise ValidationError("Discontinued must be Yes (1) or No (0).")
        return discontinued
