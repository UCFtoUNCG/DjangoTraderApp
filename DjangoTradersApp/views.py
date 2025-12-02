from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from datetime import date
from .models import Customers, Orders, Products, OrderDetails, Employees, Shippers
from .forms import CustomerSelectionForm, ProductSelectionForm, OrderDetailsForm, ProductForm


# Home view for DjangoTradersApp
def home(request):
    return render(request, "DjangoTradersApp/welcome.html")


# Products list view
class ProductsListView(ListView):
    model = Products
    template_name = "DjangoTradersApp/Products/index.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(product_name__icontains=search) |
                Q(category__category_name__icontains=search) |
                Q(supplier__company_name__icontains=search) |
                Q(quantity_per_unit__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        return context


# Product detail view
class ProductDetailView(DetailView):
    model = Products
    template_name = "DjangoTradersApp/Products/details.html"
    context_object_name = "product"
    pk_url_kwarg = "product_id"


# Product create view
class ProductCreateView(CreateView):
    """View for creating a new product."""
    model = Products
    form_class = ProductForm
    template_name = "DjangoTradersApp/Products/create.html"
    success_url = reverse_lazy('DjTraders.Products')

    def form_valid(self, form):
        messages.success(self.request, f"Product '{form.instance.product_name}' has been created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# Product update view
class ProductUpdateView(UpdateView):
    """View for updating an existing product."""
    model = Products
    form_class = ProductForm
    template_name = "DjangoTradersApp/Products/edit.html"
    pk_url_kwarg = "product_id"

    def get_success_url(self):
        return reverse_lazy('DjTraders.ProductDetail', kwargs={'product_id': self.object.product_id})

    def form_valid(self, form):
        messages.success(self.request, f"Product '{form.instance.product_name}' has been updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# Orders list view for a customer
class OrdersListView(DetailView):
    model = Customers
    template_name = "DjangoTradersApp/Customers/OrdersList.html"
    context_object_name = "customer"
    pk_url_kwarg = "customer_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        orders = customer.get_orders()
        context['orders'] = orders
        return context


# region Function-based customer views
def CustomersList(request):
    """
    View function to display all customers, optionally filtered by search.
    Supports case-insensitive, partial search on company_name, contact_title, and country.
    """
    customers = Customers.objects.all()
    
    customer_search = request.GET.get("customer", "")
    title_search = request.GET.get("title", "")
    country_search = request.GET.get("country", "")

    if customer_search:
        customers = customers.filter(company_name__icontains=customer_search)
    if title_search:
        customers = customers.filter(contact_title__icontains=title_search)
    if country_search:
        customers = customers.filter(country__iexact=country_search)

    return render(
        request=request,
        template_name="DjangoTradersApp/Customers/List.html",
        context={
            "customers": customers,
            "search_customer": customer_search,
            "search_title": title_search,
            "search_country": country_search,
            "available_countries": Customers.get_all_countries(),
        },
    )


def CustomerDetail(request, customer_id):
    """
    View function to display the details of a specific customer.
    The context includes the customer object identified by customer_id.
    The data will be displayed in the customer_detail.html template.
    """
    customer = Customers.objects.get(customer_id=customer_id)
    orders = Orders.objects.filter(customer=customer)
    products = Products.objects.filter(orderdetails__order__in=orders).distinct()
    return render(
        request=request,
        template_name="DjangoTradersApp/Customers/Detail.html",
        context={
            "customer": customer,
            "orders": orders,
            "products": products,
            "orders_count": orders.count(),
            "products_count": products.count(),
        },
    )

# endregion Function-based customer views


# region Class-based Customer views

class CustomerListView(ListView):
    """
    View to list all customers with search functionality.
    Supports case-insensitive, partial search on company_name, contact_title, and country.
    """
    model = Customers
    template_name = "DjangoTradersApp/Customers/Index.html"
    context_object_name = "customers"
    paginate_by = 10  # Paginate results, 10 per page

    def get_queryset(self):
        """
        Get the filtered queryset based on search criteria.
        Uses icontains for partial/case-insensitive matching.
        """
        queryset = super().get_queryset()

        customer_search = self.request.GET.get("customer", "")
        title_search = self.request.GET.get("title", "")
        country_search = self.request.GET.get("country", "")

        if customer_search:
            queryset = queryset.filter(company_name__icontains=customer_search)
        if title_search:
            queryset = queryset.filter(contact_title__icontains=title_search)
        if country_search:
            queryset = queryset.filter(country__iexact=country_search)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add search criteria and available countries to the context.
        """
        context = super().get_context_data(**kwargs)
        context["search_country"] = self.request.GET.get("country", "")
        context["search_customer"] = self.request.GET.get("customer", "")
        context["search_title"] = self.request.GET.get("title", "")
        context["available_countries"] = Customers.get_all_countries()
        return context


class CustomerDetailView(DetailView):
    model = Customers
    template_name = "DjangoTradersApp/Customers/Detail.html"
    context_object_name = "customer"
    pk_url_kwarg = "customer_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        # Orders placed
        orders = customer.get_orders()
        context['orders'] = orders
        context['orders_count'] = customer.get_order_count()
        # Products purchased
        products = customer.get_ordered_products()
        context['products'] = products
        context['products_count'] = products.count() if hasattr(products, 'count') else len(products)
        # Order details for product table
        order_ids = list(orders.values_list('order_id', flat=True))
        order_details = OrderDetails.objects.filter(order_id__in=order_ids)
        context['order_details'] = order_details
        return context

# endregion Class-based Customer views


# region Order Placement Views

def order_create(request, customer_id=None):
    """
    Multi-step order creation view.
    Step 1: Select customer (if not provided)
    Step 2: Add products to order
    Step 3: Enter order details (employee, shipper, required date)
    """
    # Initialize session data for order if not exists
    if 'order_data' not in request.session:
        request.session['order_data'] = {
            'customer_id': None,
            'products': [],
            'order_details': {}
        }
    
    order_data = request.session['order_data']
    
    # If customer_id is provided in URL, set it
    if customer_id:
        customer = get_object_or_404(Customers, customer_id=customer_id)
        order_data['customer_id'] = customer_id
        request.session.modified = True
    
    # Get current step from request
    step = request.GET.get('step', '1')
    
    # Step 1: Customer Selection
    if step == '1' and not order_data['customer_id']:
        if request.method == 'POST':
            form = CustomerSelectionForm(request.POST)
            if form.is_valid():
                order_data['customer_id'] = form.cleaned_data['customer'].customer_id
                request.session.modified = True
                return redirect('DjTraders.OrderCreate')
        else:
            form = CustomerSelectionForm()
        
        return render(request, 'DjangoTradersApp/Orders/create.html', {
            'step': 1,
            'form': form,
            'title': 'Select Customer'
        })
    
    # If we have a customer, proceed to product selection
    if not order_data['customer_id']:
        return redirect('DjTraders.OrderCreate')
    
    customer = get_object_or_404(Customers, customer_id=order_data['customer_id'])
    
    # Step 2: Product Selection
    if step == '2' or (step == '1' and order_data['customer_id']):
        if request.method == 'POST':
            action = request.POST.get('action', '')
            
            if action == 'add_product':
                form = ProductSelectionForm(request.POST)
                if form.is_valid():
                    product = form.cleaned_data['product']
                    quantity = form.cleaned_data['quantity']
                    discount = form.cleaned_data['discount']
                    
                    # Check if product already in cart
                    existing = next(
                        (p for p in order_data['products'] if p['product_id'] == product.product_id),
                        None
                    )
                    if existing:
                        existing['quantity'] += quantity
                    else:
                        order_data['products'].append({
                            'product_id': product.product_id,
                            'product_name': product.product_name,
                            'unit_price': product.unit_price,
                            'quantity': quantity,
                            'discount': discount
                        })
                    request.session.modified = True
                    messages.success(request, f'Added {product.product_name} to order.')
            
            elif action == 'remove_product':
                product_id = int(request.POST.get('product_id', 0))
                order_data['products'] = [
                    p for p in order_data['products'] if p['product_id'] != product_id
                ]
                request.session.modified = True
                messages.info(request, 'Product removed from order.')
            
            elif action == 'proceed':
                if order_data['products']:
                    return redirect(reverse('DjTraders.OrderCreate') + '?step=3')
                else:
                    messages.error(request, 'Please add at least one product to the order.')
        
        form = ProductSelectionForm()
        
        # Calculate cart totals
        cart_items = []
        cart_total = 0
        for item in order_data['products']:
            line_total = item['unit_price'] * item['quantity'] * (1 - item['discount'] / 100)
            cart_items.append({**item, 'line_total': line_total})
            cart_total += line_total
        
        return render(request, 'DjangoTradersApp/Orders/create.html', {
            'step': 2,
            'form': form,
            'customer': customer,
            'cart_items': cart_items,
            'cart_total': cart_total,
            'title': 'Add Products'
        })
    
    # Step 3: Order Details
    if step == '3':
        if not order_data['products']:
            messages.error(request, 'Please add products to your order first.')
            return redirect(reverse('DjTraders.OrderCreate') + '?step=2')
        
        if request.method == 'POST':
            form = OrderDetailsForm(request.POST, customer=customer)
            if form.is_valid():
                order_data['order_details'] = {
                    'employee_id': form.cleaned_data['employee'].employee_id,
                    'required_date': form.cleaned_data['required_date'].isoformat(),
                    'shipper_id': form.cleaned_data['shipper'].shipper_id,
                    'ship_name': form.cleaned_data['ship_name'],
                    'ship_address': form.cleaned_data['ship_address'],
                    'ship_city': form.cleaned_data['ship_city'],
                    'ship_region': form.cleaned_data['ship_region'],
                    'ship_postal_code': form.cleaned_data['ship_postal_code'],
                    'ship_country': form.cleaned_data['ship_country'],
                }
                request.session.modified = True
                return redirect('DjTraders.OrderConfirm')
        else:
            form = OrderDetailsForm(customer=customer)
        
        return render(request, 'DjangoTradersApp/Orders/create.html', {
            'step': 3,
            'form': form,
            'customer': customer,
            'title': 'Order Details'
        })
    
    # Default: redirect to step 2 (product selection) if customer is set
    return redirect(reverse('DjTraders.OrderCreate') + '?step=2')


def order_confirm(request):
    """
    Order confirmation view - review order before saving.
    """
    if 'order_data' not in request.session:
        messages.error(request, 'No order data found. Please start a new order.')
        return redirect('DjTraders.OrderCreate')
    
    order_data = request.session['order_data']
    
    if not order_data.get('customer_id'):
        messages.error(request, 'Please select a customer first.')
        return redirect('DjTraders.OrderCreate')
    
    if not order_data.get('products'):
        messages.error(request, 'Please add products to your order.')
        return redirect(reverse('DjTraders.OrderCreate') + '?step=2')
    
    if not order_data.get('order_details'):
        messages.error(request, 'Please complete order details.')
        return redirect(reverse('DjTraders.OrderCreate') + '?step=3')
    
    customer = get_object_or_404(Customers, customer_id=order_data['customer_id'])
    employee = get_object_or_404(Employees, employee_id=order_data['order_details']['employee_id'])
    shipper = get_object_or_404(Shippers, shipper_id=order_data['order_details']['shipper_id'])
    
    # Calculate totals
    cart_items = []
    cart_total = 0
    for item in order_data['products']:
        line_total = item['unit_price'] * item['quantity'] * (1 - item['discount'] / 100)
        cart_items.append({**item, 'line_total': line_total})
        cart_total += line_total
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'confirm':
            # Generate new order ID (find max and add 1)
            max_order = Orders.objects.order_by('-order_id').first()
            new_order_id = (max_order.order_id + 1) if max_order else 1
            
            # Create the order
            order = Orders(
                order_id=new_order_id,
                customer=customer,
                employee=employee,
                order_date=date.today(),
                required_date=date.fromisoformat(order_data['order_details']['required_date']),
                ship_via=shipper,
                freight=0,  # Could calculate based on shipper rates
                ship_name=order_data['order_details']['ship_name'],
                ship_address=order_data['order_details']['ship_address'],
                ship_city=order_data['order_details']['ship_city'],
                ship_region=order_data['order_details']['ship_region'],
                ship_postal_code=order_data['order_details']['ship_postal_code'],
                ship_country=order_data['order_details']['ship_country'],
            )
            order.save()
            
            # Create order details for each product
            for item in order_data['products']:
                order_detail = OrderDetails(
                    order_id=new_order_id,
                    product_id=item['product_id'],
                    unit_price=item['unit_price'],
                    quantity=item['quantity'],
                    discount=item['discount']
                )
                order_detail.save()
            
            # Clear session data
            del request.session['order_data']
            
            messages.success(request, f'Order #{new_order_id} has been placed successfully!')
            return redirect('DjTraders.OrderSuccess', order_id=new_order_id)
        
        elif action == 'cancel':
            del request.session['order_data']
            messages.info(request, 'Order cancelled.')
            return redirect('DjTraders.Products')
    
    return render(request, 'DjangoTradersApp/Orders/confirm.html', {
        'customer': customer,
        'employee': employee,
        'shipper': shipper,
        'order_details': order_data['order_details'],
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


def order_success(request, order_id):
    """
    Order success page - displays order confirmation.
    """
    order = get_object_or_404(Orders, order_id=order_id)
    order_details = OrderDetails.objects.filter(order_id=order_id)
    
    # Calculate total
    total = sum(
        detail.unit_price * detail.quantity * (1 - detail.discount / 100)
        for detail in order_details
    )
    
    return render(request, 'DjangoTradersApp/Orders/success.html', {
        'order': order,
        'order_details': order_details,
        'total': total,
    })


def order_cancel(request):
    """
    Cancel the current order and clear session data.
    """
    if 'order_data' in request.session:
        del request.session['order_data']
    messages.info(request, 'Order cancelled.')
    return redirect('DjTraders.Products')

# endregion Order Placement Views
