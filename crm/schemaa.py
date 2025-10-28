import re
import decimal
from django.db import transaction
from django.utils import timezone
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# -------------------------------
# GraphQL Types
# -------------------------------

# === Non-relay types (for mutations) ===
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# === Relay Nodes (for filtering and pagination) ===
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


# -------------------------------
# Error Object
# -------------------------------
class ErrorType(graphene.ObjectType):
    field = graphene.String()
    message = graphene.String()


# -------------------------------
# Input Types
# -------------------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()
    address = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)
    

# -------------------------------
# Mutations
# -------------------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(ErrorType)

    @staticmethod
    def mutate(root, info, input: CustomerInput):
        errors = []

        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append(ErrorType(field="email", message="Email already exists."))

        # Validate phone format (if provided)
        if input.phone:
            phone_pattern = re.compile(r"^(\+\d{1,15}|(\d{3}-\d{3}-\d{4}))$")
            if not phone_pattern.match(input.phone):
                errors.append(ErrorType(field="phone", message="Invalid phone format. Use +1234567890 or 123-456-7890."))

        if errors:
            return CreateCustomer(customer=None, success=False, message="Validation failed.", errors=errors)

        customer = Customer.objects.create(
            name=input.name.strip(),
            email=input.email.strip(),
            phone=(input.phone.strip() if input.phone else None)
        )
        customer.save()

        return CreateCustomer(customer=customer, success=True, message="Customer created successfully.", errors=[])


# -------------------------------
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(ErrorType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        created = []
        errors = []

        if not input:
            return BulkCreateCustomers(
                created_customers=[],
                errors=[ErrorType(message="No input provided.")],
                message="Empty input list."
            )

        with transaction.atomic():
            for idx, data in enumerate(input):
                local_errors = []
                if Customer.objects.filter(email=data.email).exists():
                    local_errors.append(f"Duplicate email: {data.email}")

                if data.phone:
                    pattern = re.compile(r"^(\+\d{1,15}|(\d{3}-\d{3}-\d{4}))$")
                    if not pattern.match(data.phone):
                        local_errors.append(f"Invalid phone format for {data.email}")

                if local_errors:
                    errors.append(ErrorType(
                        field=f"customer[{idx}]",
                        message=", ".join(local_errors)
                    ))
                    continue

                try:
                    cust = Customer.objects.create(
                        name=data.name.strip(),
                        email=data.email.strip(),
                        phone=(data.phone.strip() if data.phone else None)
                    )
                    created.append(cust)

                    for customer in cust:
                        customer.save()

                except Exception as e:
                    errors.append(ErrorType(
                        field=f"customer[{idx}]",
                        message=str(e)
                    ))


        msg = "Some customers created successfully." if errors else "All customers created successfully."


        return BulkCreateCustomers(customers=created, errors=errors, message=msg)


# -------------------------------
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(ErrorType)
    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input: ProductInput):
        errors = []

        # Validate price
        try:
            price = float(input.price)
            if price <= 0:
                errors.append(ErrorType(field="price", message="Price must be a positive number."))
        except Exception:
            errors.append(ErrorType(field="price", message="Invalid decimal format for price."))

        # Validate stock
        if input.stock is not None and input.stock < 0:
            errors.append(ErrorType(field="stock", message="Stock cannot be negative."))

        if errors:
            return CreateProduct(product=None, success=False, errors=errors)

        product = Product.objects.create(
            name=input.name.strip(),
            price=price,
            stock=input.stock or 0
        )
        
        # ✅ Save explicitly
        product.save()

        return CreateProduct(product=product, success=True, errors=[])


# -------------------------------
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(ErrorType)
    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input: OrderInput):
        errors = []

        # Validate customer
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            errors.append(ErrorType(field="customer_id", message="Invalid customer ID."))

        # Validate products
        if not input.product_ids:
            errors.append(ErrorType(field="product_ids", message="At least one product ID is required."))
            return CreateOrder(order=None, success=False, errors=errors)

        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            invalid_ids = set(input.product_ids) - set(str(p.id) for p in products)
            errors.append(ErrorType(field="product_ids", message=f"Invalid product IDs: {', '.join(invalid_ids)}"))

        if errors:
            return CreateOrder(order=None, success=False, errors=errors)

        # Calculate total
        total = sum([p.price for p in products])
        order_date = input.order_date or timezone.now()

        # Create order
        order = Order.objects.create(
            customer=customer,
            order_date=order_date,
            total_amount=total
        )
        order.products.set(products)
        # Create order

        # ✅ Save explicitly
        order.save()


        return CreateOrder(order=order, success=True, errors=[])
    
    # -------------------------------
# Delete Customer
# -------------------------------
class DeleteCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(ErrorType)

    @staticmethod
    def mutate(root, info, id):
        try:
            customer = Customer.objects.get(pk=id)
            customer.delete()
            return DeleteCustomer(success=True, message="Customer deleted successfully.", errors=[])
        except Customer.DoesNotExist:
            return DeleteCustomer(
                success=False,
                message="Customer not found.",
                errors=[ErrorType(field="id", message="Invalid customer ID.")]
            )


# -------------------------------
# Delete Product
# -------------------------------
class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(ErrorType)

    @staticmethod
    def mutate(root, info, id):
        try:
            product = Product.objects.get(pk=id)
            product.delete()
            return DeleteProduct(success=True, message="Product deleted successfully.", errors=[])
        except Product.DoesNotExist:
            return DeleteProduct(
                success=False,
                message="Product not found.",
                errors=[ErrorType(field="id", message="Invalid product ID.")]
            )

# -------------------------------
# Delete Order
# -------------------------------
class DeleteOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(ErrorType)

    @staticmethod
    def mutate(root, info, id):
        try:
            order = Order.objects.get(pk=id)
            order.delete()
            return DeleteOrder(success=True, message="Order deleted successfully.", errors=[])
        except Order.DoesNotExist:
            return DeleteOrder(
                success=False,
                message="Order not found.",
                errors=[ErrorType(field="id", message="Invalid order ID.")]
            )



# -------------------------------
# Root Mutation and Query
# -------------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

    # 🧹 Deletion mutations
    delete_customer = DeleteCustomer.Field()
    delete_product = DeleteProduct.Field()
    delete_order = DeleteOrder.Field()

class Query(graphene.ObjectType):

    # Relay Filterable Queries
    customer = graphene.relay.Node.Field(CustomerNode)
    all_customers = DjangoFilterConnectionField(CustomerNode)

    product = graphene.relay.Node.Field(ProductNode)
    all_products = DjangoFilterConnectionField(ProductNode)

    order = graphene.relay.Node.Field(OrderNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    # Basic Queries (if you want non-relay access)
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.prefetch_related('products').all()
