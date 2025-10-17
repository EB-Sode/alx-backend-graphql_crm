import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    # Basic filters
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')

    # Date range filters
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    # Challenge: Filter by phone number pattern (e.g., starts with +1)
    phone_starts_with = django_filters.CharFilter(method='filter_phone_pattern')

    def filter_phone_pattern(self, queryset, name, value):
        """Custom filter to match customers whose phone starts with a specific pattern."""
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at']


class ProductFilter(django_filters.FilterSet):
    # Basic filters
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    # Range filters
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')

    # Challenge: Filter products with low stock (e.g., stock < 10)
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    def filter_low_stock(self, queryset, name, value):
        """Return only low-stock products if True."""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']


class OrderFilter(django_filters.FilterSet):
    # Range filters
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date__gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date__lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')

    # Related field lookups
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')

    # Challenge: Filter orders that include a specific product ID
    product_id = django_filters.NumberFilter(method='filter_by_product_id')

    def filter_by_product_id(self, queryset, name, value):
        """Return orders that include a specific product ID."""
        return queryset.filter(products__id=value).distinct()

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date', 'customer_name', 'product_name']
