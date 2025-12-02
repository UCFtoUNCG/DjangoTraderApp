from django.test import TestCase, Client, override_settings
from django.urls import reverse
from .models import Products, Categories, Suppliers
from .forms import ProductForm


# These tests focus on form validation logic and don't require database access
class ProductFormValidationTest(TestCase):
    """Tests for ProductForm field validation (no database required)."""

    def test_empty_product_name_invalid(self):
        """Test that empty product name fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': '',
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('product_name', form.errors)

    def test_whitespace_product_name_invalid(self):
        """Test that whitespace-only product name fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': '   ',
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('product_name', form.errors)

    def test_negative_unit_price_invalid(self):
        """Test that negative unit price fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': 'Test Product',
            'unit_price': -10.00,
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('unit_price', form.errors)

    def test_negative_units_in_stock_invalid(self):
        """Test that negative units in stock fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': 'Test Product',
            'units_in_stock': -5,
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('units_in_stock', form.errors)

    def test_negative_units_on_order_invalid(self):
        """Test that negative units on order fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': 'Test Product',
            'units_on_order': -3,
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('units_on_order', form.errors)

    def test_negative_reorder_level_invalid(self):
        """Test that negative reorder level fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': 'Test Product',
            'reorder_level': -1,
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('reorder_level', form.errors)

    def test_product_name_too_long_invalid(self):
        """Test that product name longer than 40 characters fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': 'A' * 41,  # 41 characters
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('product_name', form.errors)

    def test_quantity_per_unit_too_long_invalid(self):
        """Test that quantity per unit longer than 20 characters fails validation."""
        form_data = {
            'product_id': 9999,
            'product_name': 'Test Product',
            'quantity_per_unit': 'A' * 21,  # 21 characters
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity_per_unit', form.errors)

    def test_product_id_zero_invalid(self):
        """Test that product_id of 0 fails validation."""
        form_data = {
            'product_id': 0,
            'product_name': 'Test Product',
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('product_id', form.errors)

    def test_product_id_negative_invalid(self):
        """Test that negative product_id fails validation."""
        form_data = {
            'product_id': -1,
            'product_name': 'Test Product',
            'discontinued': 0,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('product_id', form.errors)

    def test_form_has_expected_fields(self):
        """Test that form contains all expected fields."""
        form = ProductForm()
        expected_fields = [
            'product_id', 'product_name', 'supplier', 'category',
            'quantity_per_unit', 'unit_price', 'units_in_stock',
            'units_on_order', 'reorder_level', 'discontinued'
        ]
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_form_widgets_have_form_control_class(self):
        """Test that form widgets have Bootstrap form-control class."""
        form = ProductForm()
        for field_name, field in form.fields.items():
            widget_class = field.widget.attrs.get('class', '')
            self.assertIn('form-control', widget_class,
                         f"Field '{field_name}' should have 'form-control' class")


class ProductURLPatternsTest(TestCase):
    """Tests for URL patterns (no database required)."""

    def test_product_create_url_pattern(self):
        """Test that the create URL pattern is correct."""
        url = reverse('DjTraders.ProductCreate')
        self.assertEqual(url, '/DjTraders/Products/Create/')

    def test_product_edit_url_pattern(self):
        """Test that the edit URL pattern is correct."""
        url = reverse('DjTraders.ProductEdit', kwargs={'product_id': '1'})
        self.assertEqual(url, '/DjTraders/Products/1/Edit/')

