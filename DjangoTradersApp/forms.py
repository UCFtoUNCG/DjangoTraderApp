from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Customers, Products, Employees, Shippers, Orders, OrderDetails


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
