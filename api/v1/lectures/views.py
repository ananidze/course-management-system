from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from django.db import models
from rest_framework.views import PermissionDenied

from api.core.permissions import (
    IsLectureTeacher,
)

from lectures.models import Lecture
from homework.models import Homework
from api.core.responses import APIResponse
from api.core.documentation import (
    CommonResponses,
    CommonParameters,
)
from api.core.exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
)
from api.core.pagination import StandardResultsSetPagination
from .serializers import (
    LectureSerializer,
    LectureCreateSerializer,
    LectureUpdateSerializer,
    LectureDetailSerializer,
    LectureListSerializer,
)
from api.v1.homework.serializers import (
    HomeworkCreateSerializer,
    HomeworkUpdateSerializer,
    HomeworkDetailSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Lectures",
        description=("Retrieve a paginated list of lectures based on user role"),
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.SEARCH,
            CommonParameters.ORDERING,
        ],
        responses={
            200: LectureListSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["lectures"],
    ),
    create=extend_schema(
        summary="Create Lecture",
        description="Create a new lecture for a course (course teachers only)",
        request=LectureCreateSerializer,
        responses={
            201: LectureDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["lectures"],
    ),
    retrieve=extend_schema(
        summary="Get Lecture",
        description="Retrieve a specific lecture by ID",
        responses={
            200: LectureDetailSerializer,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    ),
    update=extend_schema(
        summary="Update Lecture",
        description="Update a specific lecture by ID (course teachers only)",
        request=LectureUpdateSerializer,
        responses={
            200: LectureDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Lecture",
        description="Partially update a specific lecture by ID (course teachers only)",
        request=LectureUpdateSerializer,
        responses={
            200: LectureDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    ),
    destroy=extend_schema(
        summary="Delete Lecture",
        description="Delete a specific lecture by ID (course teachers only)",
        responses={
            204: CommonResponses.SUCCESS_RESPONSE,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    ),
)
class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsLectureTeacher]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return LectureCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return LectureUpdateSerializer
        elif self.action == "retrieve":
            return LectureDetailSerializer
        elif self.action == "list":
            return LectureListSerializer
        return LectureSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == user.Role.TEACHER:
            return (
                Lecture.objects.filter(
                    models.Q(course__teacher=user) | models.Q(course__teachers=user)
                )
                .select_related("course", "course__teacher")
                .prefetch_related("course__teachers", "course__students")
                .distinct()
            )
        elif user.role == user.Role.STUDENT:
            return (
                Lecture.objects.filter(course__students=user)
                .select_related("course", "course__teacher")
                .prefetch_related("course__teachers", "course__students")
            )
        else:
            return (
                Lecture.objects.all()
                .select_related("course", "course__teacher")
                .prefetch_related("course__teachers", "course__students")
            )

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        course = instance.course

        if not (user == course.teacher or user in course.teachers.all()):
            raise PermissionDenied("Only course teachers can delete lectures.")

        instance.delete()

    @extend_schema(
        summary="Create Homework for Lecture",
        description=("Create a new homework assignment for a specific lecture"),
        request=HomeworkCreateSerializer,
        responses={
            201: HomeworkDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    )
    @action(detail=True, methods=["post"], url_path="homework")
    def create_homework(self, request, pk=None):  # noqa: ARG002
        try:
            lecture = self.get_object()
            user = request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can create homework for this lecture."
                )

            serializer = HomeworkCreateSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                homework = serializer.save(lecture=lecture)
                return APIResponse.created(
                    data=HomeworkDetailSerializer(homework).data,
                    message="Homework created successfully",
                )
            return APIResponse.validation_error(
                errors=serializer.errors, message="Homework creation failed"
            )
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    @extend_schema(
        summary="Update Homework for Lecture",
        description=(
            "Update a specific homework assignment for a lecture (teachers only)"
        ),
        request=HomeworkUpdateSerializer,
        responses={
            200: HomeworkDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    )
    @action(detail=True, methods=["put"], url_path="homework/(?P<homework_id>[^/.]+)")
    def update_homework(self, request, pk=None, homework_id=None):  # noqa: ARG002
        try:
            lecture = self.get_object()
            user = request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can update homework for this lecture."
                )

            try:
                homework = Homework.objects.select_related(
                    "lecture", "lecture__course"
                ).get(id=homework_id, lecture=lecture)
            except Homework.DoesNotExist:
                raise ResourceNotFoundException("Homework not found")

            serializer = HomeworkUpdateSerializer(
                homework, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                updated_homework = serializer.save()
                return APIResponse.updated(
                    data=HomeworkDetailSerializer(updated_homework).data,
                    message="Homework updated successfully",
                )
            return APIResponse.validation_error(
                errors=serializer.errors, message="Homework update failed"
            )
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    @extend_schema(
        summary="Delete Homework from Lecture",
        description=(
            "Delete a specific homework assignment from a lecture (teachers only)"
        ),
        responses={
            204: CommonResponses.SUCCESS_RESPONSE,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    )
    @action(
        detail=True, methods=["delete"], url_path="homework/(?P<homework_id>[^/.]+)"
    )
    def delete_homework(self, request, pk=None, homework_id=None):  # noqa: ARG002
        try:
            lecture = self.get_object()
            user = request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can delete homework for this lecture."
                )

            try:
                homework = Homework.objects.select_related(
                    "lecture", "lecture__course"
                ).get(id=homework_id, lecture=lecture)
            except Homework.DoesNotExist:
                raise ResourceNotFoundException("Homework not found")

            homework.delete()
            return APIResponse.deleted("Homework deleted successfully")
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    @extend_schema(
        summary="List Homework for Lecture",
        description="Retrieve all homework assignments for a specific lecture",
        responses={
            200: HomeworkDetailSerializer(many=True),
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    )
    @action(detail=True, methods=["get"], url_path="homework")
    def list_homework(self, request, pk=None):  # noqa: ARG002
        try:
            lecture = self.get_object()
            user = request.user

            if not lecture.course.can_access(user):
                raise PermissionDeniedException(
                    "You don't have permission to access this lecture."
                )

            homework_list = lecture.homework_assignments.select_related(
                "lecture", "lecture__course"
            ).all()
            serializer = HomeworkDetailSerializer(homework_list, many=True)
            return APIResponse.success(
                data=serializer.data,
                message="Homework list retrieved successfully",
            )
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    @extend_schema(
        summary="Get Homework for Lecture",
        description="Retrieve a specific homework assignment for a lecture",
        responses={
            200: HomeworkDetailSerializer,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    )
    @action(detail=True, methods=["get"], url_path="homework/(?P<homework_id>[^/.]+)")
    def get_homework(self, request, pk=None, homework_id=None):  # noqa: ARG002
        try:
            lecture = self.get_object()
            user = request.user

            if not lecture.course.can_access(user):
                raise PermissionDeniedException(
                    "You don't have permission to access this lecture."
                )

            try:
                homework = Homework.objects.select_related(
                    "lecture", "lecture__course"
                ).get(id=homework_id, lecture=lecture)
            except Homework.DoesNotExist:
                raise ResourceNotFoundException("Homework not found")

            serializer = HomeworkDetailSerializer(homework)
            return APIResponse.success(
                data=serializer.data,
                message="Homework retrieved successfully",
            )
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")
