import graphene
from graphene_django import DjangoObjectType
from crm.models import Product  # ✅ required import


# --- Define ProductType (GraphQL representation of Product model) ---
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock", "price")  # adjust fields as in your model


# --- Define the Mutation for updating low-stock products ---
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no arguments required

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        # Find products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)

        updated = []
        for product in low_stock_products:
            product.stock += 10  # ✅ restock by 10
            product.save()
            updated.append(product)

        message = (
            f"{len(updated)} product(s) restocked successfully."
            if updated else "No products required restocking."
        )

        return UpdateLowStockProducts(updated_products=updated, message=message)


# --- Root Query (if not already defined elsewhere) ---
class Query(graphene.ObjectType):
    products = graphene.List(ProductType)

    def resolve_products(self, info):
        return Product.objects.all()


# --- Root Mutation ---
class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()


# --- Final Schema ---
schema = graphene.Schema(query=Query, mutation=Mutation)
