import graphene
from .models import Product  # assuming you have a Product model
from .types import ProductType  # assuming you defined a ProductType in schema


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # No arguments needed

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        # Query products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)

        updated = []
        for product in low_stock_products:
            product.stock += 10  # simulate restocking
            product.save()
            updated.append(product)

        msg = (
            f"{len(updated)} product(s) restocked successfully."
            if updated else "No products required restocking."
        )

        return UpdateLowStockProducts(updated_products=updated, message=msg)


# --- Integrate mutation into your schema ---
class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
