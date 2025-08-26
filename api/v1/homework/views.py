from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from django.db import models

from api.core.permissions import (
    IsHomeworkTeacher,
    IsHomeworkStudent,
)

from homework.models import Homework, HomeworkSubmission
from api.core.responses import APIResponse
from api.core.documentation import (
    CommonResponses,
    CommonParameters,
)
from api.core.exceptions import (
    PermissionDeniedException,
    BusinessLogicException,
    ResourceNotFoundException,
)
from api.core.pagination import StandardResultsSetPagination
from .serializers import (
    HomeworkSerializer,
    HomeworkCreateSerializer,
    HomeworkUpdateSerializer,
    HomeworkDetailSerializer,
    HomeworkListSerializer,
    HomeworkSubmissionCreateSerializer,
    HomeworkSubmissionDetailSerializer,
    GradeCreateSerializer,
    GradeUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Homework",
        description="Retrieve a paginated list of homework assignments based on user role and course enrollment",
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.SEARCH,
            CommonParameters.ORDERING,
        ],
        responses={
            200: HomeworkListSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["homework"],
    ),
    create=extend_schema(
        summary="Create Homework",
        description="Create a new homework assignment for a lecture (course teachers only)",
        request=HomeworkCreateSerializer,
        responses={
            201: HomeworkDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["homework"],
    ),
    retrieve=extend_schema(
        summary="Get Homework",
        description="Retrieve a specific homework assignment by ID",
        responses={
            200: HomeworkDetailSerializer,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    ),
    update=extend_schema(
        summary="Update Homework",
        description="Update a specific homework assignment by ID (course teachers only)",
        request=HomeworkUpdateSerializer,
        responses={
            200: HomeworkDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Homework",
        description="Partially update a homework (teachers only)",
        request=HomeworkUpdateSerializer,
        responses={
            200: HomeworkDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    ),
    destroy=extend_schema(
        summary="Delete Homework",
        description="Delete a specific homework assignment by ID (course teachers only)",
        responses={
            204: CommonResponses.SUCCESS_RESPONSE,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["homework"],
    ),
)
class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.select_related(
        "lecture__course__teacher"
    ).prefetch_related("lecture__course__teachers", "lecture__course__students")
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsHomeworkTeacher]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action == "submit_homework":
            permission_classes = [IsHomeworkStudent]
        elif self.action == "get_submissions":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return HomeworkCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return HomeworkUpdateSerializer
        elif self.action == "retrieve":
            return HomeworkDetailSerializer
        elif self.action == "list":
            return HomeworkListSerializer
        return HomeworkSerializer

    def get_queryset(self):
        user = self.request.user

        base_queryset = Homework.objects.select_related(
            "lecture__course__teacher"
        ).prefetch_related("lecture__course__teachers", "lecture__course__students")

        if user.is_teacher:
            return base_queryset.filter(
                models.Q(lecture__course__teacher=user)
                | models.Q(lecture__course__teachers=user)
            ).distinct()
        elif user.is_student:
            return base_queryset.filter(lecture__course__students=user)
        else:
            return base_queryset.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return APIResponse.success(
                data=serializer.data,
                message="Homework list retrieved successfully",
                meta=self.paginator.get_paginated_response_data(serializer.data),
            )

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data, message="Homework list retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            homework = serializer.save()
            return APIResponse.created(
                data=HomeworkDetailSerializer(homework).data,
                message="Homework created successfully",
            )
        return APIResponse.validation_error(
            errors=serializer.errors, message="Homework creation failed"
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            homework = self.get_object()
            serializer = self.get_serializer(homework)
            return APIResponse.success(
                data=serializer.data, message="Homework retrieved successfully"
            )
        except Homework.DoesNotExist:
            raise ResourceNotFoundException("Homework not found")

    def update(self, request, *args, **kwargs):
        try:
            homework = self.get_object()
            serializer = self.get_serializer(homework, data=request.data, partial=False)
            if serializer.is_valid():
                updated_homework = serializer.save()
                return APIResponse.updated(
                    data=HomeworkDetailSerializer(updated_homework).data,
                    message="Homework updated successfully",
                )
            return APIResponse.validation_error(
                errors=serializer.errors, message="Homework update failed"
            )
        except Homework.DoesNotExist:
            raise ResourceNotFoundException("Homework not found")

    def partial_update(self, request, *args, **kwargs):
        try:
            homework = self.get_object()
            serializer = self.get_serializer(homework, data=request.data, partial=True)
            if serializer.is_valid():
                updated_homework = serializer.save()
                return APIResponse.updated(
                    data=HomeworkDetailSerializer(updated_homework).data,
                    message="Homework updated successfully",
                )
            return APIResponse.validation_error(
                errors=serializer.errors, message="Homework update failed"
            )
        except Homework.DoesNotExist:
            raise ResourceNotFoundException("Homework not found")

    def destroy(self, request, *args, **kwargs):
        try:
            homework = self.get_object()
            user = self.request.user
            course = homework.lecture.course

            if not course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can delete homework."
                )

            homework.delete()
            return APIResponse.deleted("Homework deleted successfully")
        except Homework.DoesNotExist:
            raise ResourceNotFoundException("Homework not found")

    @extend_schema(
        summary="Submit Homework",
        description="Submit homework solution for a specific assignment (students only)",
        request=HomeworkSubmissionCreateSerializer,
        responses={
            201: HomeworkSubmissionDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["submissions"],
    )
    @action(detail=True, methods=["post"], url_path="submit")
    def submit_homework(self, request, pk=None):
        try:
            homework = self.get_object()
            user = request.user

            if not user.is_student:
                raise PermissionDeniedException("Only students can submit homework.")

            if not homework.lecture.course.students.filter(id=user.id).exists():
                raise PermissionDeniedException("You are not enrolled in this course.")

            if HomeworkSubmission.objects.filter(
                homework=homework, student=user
            ).exists():
                raise BusinessLogicException(
                    "You have already submitted this homework.",
                    error_code="DUPLICATE_SUBMISSION",
                )

            serializer = HomeworkSubmissionCreateSerializer(data=request.data)
            if serializer.is_valid():
                submission = serializer.save(homework=homework, student=user)
                return APIResponse.created(
                    data=HomeworkSubmissionDetailSerializer(submission).data,
                    message="Homework submitted successfully",
                )
            return APIResponse.validation_error(
                errors=serializer.errors, message="Homework submission failed"
            )
        except Homework.DoesNotExist:
            raise ResourceNotFoundException("Homework not found")

    @extend_schema(
        summary="Get Homework Submissions",
        description="Retrieve submissions for a specific homework assignment ",
        responses={
            200: HomeworkSubmissionDetailSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["submissions"],
    )
    @action(detail=True, methods=["get"], url_path="submissions")
    def get_submissions(self, request, pk=None):
        try:
            homework = self.get_object()
            user = request.user

            if user.is_teacher:
                if not homework.lecture.course.is_teacher(user):
                    raise PermissionDeniedException(
                        "You can only view submissions for your courses."
                    )
                submissions = HomeworkSubmission.objects.filter(homework=homework)
            elif user.is_student:
                if not homework.lecture.course.students.filter(id=user.id).exists():
                    raise PermissionDeniedException(
                        "You are not enrolled in this course."
                    )
                submissions = HomeworkSubmission.objects.filter(
                    homework=homework, student=user
                )
            else:
                submissions = HomeworkSubmission.objects.none()

            page = self.paginate_queryset(submissions)
            if page is not None:
                serializer = HomeworkSubmissionDetailSerializer(page, many=True)
                return APIResponse.success(
                    data=serializer.data,
                    message="Homework submissions retrieved successfully",
                    meta=self.paginator.get_paginated_response_data(serializer.data),
                )

            serializer = HomeworkSubmissionDetailSerializer(submissions, many=True)
            return APIResponse.success(
                data=serializer.data,
                message="Homework submissions retrieved successfully",
            )
        except Homework.DoesNotExist:
            raise ResourceNotFoundException("Homework not found")


@extend_schema_view(
    list=extend_schema(
        summary="List Submissions",
        description="Retrieve a paginated list of homework submissions based on user role (teachers see all, students see their own)",
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.SEARCH,
            CommonParameters.ORDERING,
        ],
        responses={
            200: HomeworkSubmissionDetailSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["submissions"],
    ),
    retrieve=extend_schema(
        summary="Get Submission",
        description="Retrieve a specific homework submission by ID",
        responses={
            200: HomeworkSubmissionDetailSerializer,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["submissions"],
    ),
)
class HomeworkSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HomeworkSubmission.objects.select_related(
        "homework__lecture__course__teacher", "student", "grade"
    ).prefetch_related("homework__lecture__course__teachers")
    permission_classes = [IsAuthenticated]
    serializer_class = HomeworkSubmissionDetailSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action == "grade_submission":
            permission_classes = [IsHomeworkTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        base_queryset = HomeworkSubmission.objects.select_related(
            "homework__lecture__course__teacher", "student", "grade"
        ).prefetch_related("homework__lecture__course__teachers")

        if user.is_teacher:
            return base_queryset.filter(
                models.Q(homework__lecture__course__teacher=user)
                | models.Q(homework__lecture__course__teachers=user)
            ).distinct()
        elif user.is_student:
            return base_queryset.filter(student=user)
        else:
            return base_queryset.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return APIResponse.success(
                data=serializer.data,
                message="Submissions list retrieved successfully",
                meta=self.paginator.get_paginated_response_data(serializer.data),
            )

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data, message="Submissions list retrieved successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            submission = self.get_object()
            serializer = self.get_serializer(submission)
            return APIResponse.success(
                data=serializer.data, message="Submission retrieved successfully"
            )
        except HomeworkSubmission.DoesNotExist:
            raise ResourceNotFoundException("Submission not found")

    @extend_schema(
        summary="Grade Submission",
        description="Grade a homework submission (course teachers only)",
        request=GradeCreateSerializer,
        responses={
            201: HomeworkSubmissionDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["grades"],
    )
    @action(detail=True, methods=["post"], url_path="grade")
    def grade_submission(self, request, pk=None):
        try:
            submission = self.get_object()
            user = request.user

            if not user.is_teacher:
                raise PermissionDeniedException("Only teachers can grade submissions.")

            if not submission.homework.lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can grade submissions."
                )

            if hasattr(submission, "grade"):
                raise BusinessLogicException(
                    "This submission has already been graded.",
                    error_code="GRADE_ALREADY_EXISTS",
                )

            serializer = GradeCreateSerializer(data=request.data)
            if serializer.is_valid():
                grade = serializer.save(submission=submission, graded_by=user)
                return APIResponse.created(
                    data=HomeworkSubmissionDetailSerializer(submission).data,
                    message="Grade created successfully",
                )
            return APIResponse.validation_error(
                errors=serializer.errors, message="Grade creation failed"
            )
        except HomeworkSubmission.DoesNotExist:
            raise ResourceNotFoundException("Submission not found")

    @extend_schema(
        summary="Update Grade",
        description="Update a grade for a homework submission (course teachers only)",
        request=GradeUpdateSerializer,
        responses={
            200: HomeworkSubmissionDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["grades"],
    )
    @action(detail=True, methods=["put", "patch"], url_path="update-grade")
    def update_grade(self, request, pk=None):
        try:
            submission = self.get_object()
            user = request.user

            if not user.is_teacher:
                raise PermissionDeniedException("Only teachers can update grades.")

            if not submission.homework.lecture.course.is_teacher(user):
                raise PermissionDeniedException(
                    "Only course teachers can update grades."
                )

            if not hasattr(submission, "grade"):
                raise BusinessLogicException(
                    "This submission has not been graded yet.",
                    error_code="GRADE_NOT_FOUND",
                )

            serializer = GradeUpdateSerializer(
                submission.grade, data=request.data, partial=request.method == "PATCH"
            )
            if serializer.is_valid():
                serializer.save()
                return APIResponse.updated(
                    data=HomeworkSubmissionDetailSerializer(submission).data,
                    message="Grade updated successfully",
                )
            return APIResponse.validation_error(
                errors=serializer.errors, message="Grade update failed"
            )
        except HomeworkSubmission.DoesNotExist:
            raise ResourceNotFoundException("Submission not found")
