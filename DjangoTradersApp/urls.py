
from django.urls import path
from . import views

urlpatterns = [

	#region Function View URLs
	#URLs for Function based views - including Home.	
	path(
		route="",
		view=views.home,
		name="home"
	),

    path(
        'DjTraders/Customers', 
         views.CustomerListView.as_view(), 
         name='DjTraders.Customers'),

	path(
		'DjTraders/Products',
		 views.ProductsListView.as_view(),
		 name='DjTraders.Products'),

	path(
		'DjTraders/ProductDetail/<str:product_id>/',
		 views.ProductDetailView.as_view(),
		 name='DjTraders.ProductDetail'),

	path(
		'DjTraders/CustomerOrders/<str:customer_id>/',
		 views.OrdersListView.as_view(),
		 name='DjTraders.CustomerOrders'),

    path(
        'DjTraders/CustomerDetail/<str:customer_id>/', 
         views.CustomerDetailView.as_view(), 
         name='DjTraders.CustomerDetail'),

	#endregion Function View URLs

	#region Class Based View URLs
	path(
		route="customers/",
		view=views.CustomersList,
		name="CustomersList"
	),

	path(
		route="customers/<str:customer_id>/",
		view=views.CustomerDetail,
		name="CustomerDetail"
	),

	#endregion Class Based View URLs

	#region Order Placement URLs
	path(
		'DjTraders/Orders/Create/',
		views.order_create,
		name='DjTraders.OrderCreate'
	),

	path(
		'DjTraders/Orders/Create/<str:customer_id>/',
		views.order_create,
		name='DjTraders.OrderCreateForCustomer'
	),

	path(
		'DjTraders/Orders/Confirm/',
		views.order_confirm,
		name='DjTraders.OrderConfirm'
	),

	path(
		'DjTraders/Orders/Success/<int:order_id>/',
		views.order_success,
		name='DjTraders.OrderSuccess'
	),

	path(
		'DjTraders/Orders/Cancel/',
		views.order_cancel,
		name='DjTraders.OrderCancel'
	),

	#endregion Order Placement URLs
]