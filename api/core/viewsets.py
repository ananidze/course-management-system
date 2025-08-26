from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .documentation import CommonParameters, standard_responses


@extend_schema_view(
    list=extend_schema(
        summary="List Resources",
        description="Retrieve a paginated list of resources",
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.SEARCH,
            CommonParameters.ORDERING,
        ],
        responses=standard_responses(200, 401, 403),
        tags=["base"],
    ),
    create=extend_schema(
        summary="Create Resource",
        description="Create a new resource",
        responses=standard_responses(201, 400, 401, 403),
        tags=["base"],
    ),
    retrieve=extend_schema(
        summary="Get Resource",
        description="Retrieve a specific resource by ID",
        responses=standard_responses(200, 401, 403, 404),
        tags=["base"],
    ),
    update=extend_schema(
        summary="Update Resource",
        description="Update a specific resource by ID",
        responses=standard_responses(200, 400, 401, 403, 404),
        tags=["base"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Resource",
        description="Partially update a specific resource by ID",
        responses=standard_responses(200, 400, 401, 403, 404),
        tags=["base"],
    ),
    destroy=extend_schema(
        summary="Delete Resource",
        description="Delete a specific resource by ID",
        responses=standard_responses(204, 401, 403, 404),
        tags=["base"],
    ),
)
class DocumentedModelViewSet(viewsets.ModelViewSet):
    def get_schema_operation(self, path, method):
        return super().get_schema_operation(path, method)


@extend_schema_view(
    list=extend_schema(
        summary="List Resources",
        description="Retrieve a paginated list of resources",
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.SEARCH,
            CommonParameters.ORDERING,
        ],
        responses=standard_responses(200, 401, 403),
        tags=["base"],
    ),
    retrieve=extend_schema(
        summary="Get Resource",
        description="Retrieve a specific resource by ID",
        responses=standard_responses(200, 401, 403, 404),
        tags=["base"],
    ),
)
class DocumentedReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_schema_operation(self, path, method):
        return super().get_schema_operation(path, method)
