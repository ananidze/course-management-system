from rest_framework import viewsets
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


@extend_schema_view(
    list=extend_schema(
        summary="List Homework for Lecture",
        description="Retrieve all homework assignments for a specific lecture",
        responses={
            200: HomeworkDetailSerializer(many=True),
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    ),
    create=extend_schema(
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
    ),
    retrieve=extend_schema(
        summary="Get Homework for Lecture",
        description="Retrieve a specific homework assignment for a lecture",
        responses={
            200: HomeworkDetailSerializer,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    ),
    update=extend_schema(
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
    ),
    partial_update=extend_schema(
        summary="Partially Update Homework for Lecture",
        description=(
            "Partially update a specific homework assignment for a lecture (teachers only)"
        ),
        request=HomeworkUpdateSerializer,
        responses={
            200: HomeworkDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    ),
    destroy=extend_schema(
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
    ),
)
class LectureHomeworkViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        lecture_id = self.kwargs.get("lecture_pk")
        return Homework.objects.filter(lecture_id=lecture_id).select_related(
            "lecture", "lecture__course"
        )

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
            return HomeworkCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return HomeworkUpdateSerializer
        return HomeworkDetailSerializer

    def perform_create(self, serializer):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = self.request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can create homework for this lecture."
                )

            serializer.save(lecture=lecture)
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    def perform_update(self, serializer):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = self.request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can update homework for this lecture."
                )

            serializer.save()
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    def perform_destroy(self, instance):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = self.request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can delete homework for this lecture."
                )

            instance.delete()
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    def list(self, request, *args, **kwargs):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = request.user

            if not lecture.course.can_access(user):
                raise PermissionDeniedException(
                    "You don't have permission to access this lecture."
                )

            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(
                data=serializer.data,
                message="Homework list retrieved successfully",
            )
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    def retrieve(self, request, *args, **kwargs):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = request.user

            if not lecture.course.can_access(user):
                raise PermissionDeniedException(
                    "You don't have permission to access this lecture."
                )

            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(
                data=serializer.data,
                message="Homework retrieved successfully",
            )
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")

    def create(self, request, *args, **kwargs):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can create homework for this lecture."
                )

            # Create a copy of the data without the lecture field for validation
            data = request.data.copy()
            data.pop("lecture", None)  # Remove lecture field if present

            serializer = self.get_serializer(data=data, context={"request": request})
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

    def update(self, request, *args, **kwargs):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can update homework for this lecture."
                )

            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=partial,
                context={"request": request},
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

    def destroy(self, request, *args, **kwargs):
        lecture_id = self.kwargs.get("lecture_pk")
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            user = request.user

            if not lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can delete homework for this lecture."
                )

            instance = self.get_object()
            instance.delete()
            return APIResponse.deleted("Homework deleted successfully")
        except Lecture.DoesNotExist:
            raise ResourceNotFoundException("Lecture not found")
