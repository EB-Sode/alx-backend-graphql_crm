import graphene
from crm.schemaa import CRMQuery  # adjust path if different

class Query(CRMQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
