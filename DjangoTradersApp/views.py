
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from .models import Customers, Orders, Products

# Products list view

class ProductsListView(ListView):
    model = Products
    template_name = "DjangoTradersApp/Products/index.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        name_search = self.request.GET.get("name", "")
        category_search = self.request.GET.get("category", "")
        supplier_search = self.request.GET.get("supplier", "")
        if name_search:
            queryset = queryset.filter(product_name__icontains=name_search)
        if category_search:
            queryset = queryset.filter(category__category_name__icontains=category_search)
        if supplier_search:
            queryset = queryset.filter(supplier__company_name__icontains=supplier_search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_search"] = self.request.GET.get("name", "")
        context["category_search"] = self.request.GET.get("category", "")
        context["supplier_search"] = self.request.GET.get("supplier", "")
        return context

# Product detail view
class ProductDetailView(DetailView):
    model = Products
    template_name = "DjangoTradersApp/Products/details.html"
    context_object_name = "product"
    pk_url_kwarg = "product_id"

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

# Create your views here.
def home(request):
    return render(
        request=request,
        template_name="DjangoTradersApp/welcome.html",
    )

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
    paginate_by = 10 # Paginate results, 10 per page

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
        from .models import OrderDetails
        order_ids = list(orders.values_list('order_id', flat=True))
        order_details = OrderDetails.objects.filter(order_id__in=order_ids)
        context['order_details'] = order_details
        return context

# endregion Class-based Customer views