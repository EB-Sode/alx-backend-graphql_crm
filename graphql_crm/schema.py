import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


class Query(CRMQuery, graphene.ObjectType):
    """
    Root Query class combining all CRM queries.
    Extend this if you add more app-specific queries in the future.
    """
    pass


class Mutation(CRMMutation, graphene.ObjectType):
    """
    Root Mutation class combining all CRM mutations.
    Extend this if you add more app-specific mutations later.
    """
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
