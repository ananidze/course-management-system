from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db import models
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Count
from django.core.exceptions import ValidationError
from users.models import User

from api.core.responses import APIResponse
from api.core.permissions import (
    IsTeacher,
    IsCourseTeacher,
    IsCourseOwner,
)
from api.core.documentation import (
    CommonResponses,
    CommonParameters,
)
from api.core.viewsets import DocumentedModelViewSet
from api.core.pagination import StandardResultsSetPagination
from courses.models import Course
from lectures.models import Lecture
from .serializers import (
    CourseSerializer,
    CourseCreateSerializer,
    CourseUpdateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseEnrollmentSerializer,
    CourseStudentSerializer,
)
from api.v1.lectures.serializers import (
    LectureCreateSerializer,
    LectureUpdateSerializer,
    LectureDetailSerializer,
    LectureListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Courses",
        description="Retrieve a paginated list of courses based on user role",
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.SEARCH,
            CommonParameters.ORDERING,
        ],
        responses={
            200: CourseListSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["courses"],
    ),
    create=extend_schema(
        summary="Create Course",
        description="Create a new course (teachers only)",
        request=CourseCreateSerializer,
        responses={
            201: CourseDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["courses"],
    ),
    retrieve=extend_schema(
        summary="Get Course",
        description="Retrieve a specific course by ID",
        responses={
            200: CourseDetailSerializer,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    ),
    update=extend_schema(
        summary="Update Course",
        description="Update a specific course by ID (course owner only)",
        request=CourseUpdateSerializer,
        responses={
            200: CourseDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Course",
        description="Partially update a specific course by ID (course owner only)",
        request=CourseUpdateSerializer,
        responses={
            200: CourseDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    ),
    destroy=extend_schema(
        summary="Delete Course",
        description="Delete a specific course by ID (course owner only)",
        responses={
            204: CommonResponses.SUCCESS_RESPONSE,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    ),
)
class CourseViewSet(DocumentedModelViewSet):
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [IsTeacher]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsCourseOwner]
        elif self.action in [
            "add_student",
            "remove_student",
            "add_teacher",
            "remove_teacher",
            "list_students",
        ]:
            permission_classes = [IsCourseTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return CourseCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CourseUpdateSerializer
        elif self.action == "retrieve":
            return CourseDetailSerializer
        elif self.action == "list":
            return CourseListSerializer
        return CourseSerializer

    def get_queryset(self):
        user = self.request.user

        base_queryset = (
            Course.objects.select_related("teacher")
            .prefetch_related("teachers", "students")
            .annotate(
                _student_count=Count("students"), _teacher_count=Count("teachers")
            )
        )

        if user.role == user.Role.TEACHER:
            return base_queryset.filter(
                models.Q(teacher=user) | models.Q(teachers=user)
            ).distinct()
        elif user.role == user.Role.STUDENT:
            return base_queryset.filter(students=user)
        else:
            return base_queryset.all()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        course = serializer.instance
        response_serializer = CourseDetailSerializer(course)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = CourseDetailSerializer(instance)
        return Response(response_serializer.data)

    @extend_schema(
        summary="Add Student to Course",
        description="Add a student to a course (teachers only)",
        request=CourseEnrollmentSerializer,
        responses={
            200: CommonResponses.SUCCESS_RESPONSE,
            400: CommonResponses.VALIDATION_ERROR,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["courses"],
    )
    @action(detail=True, methods=["post"], url_path="add-student")
    def add_student(self, request, pk=None):
        course = self.get_object()

        serializer = CourseEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data["user_id"]

            if student.role != student.Role.STUDENT:
                return APIResponse.error(
                    message="Only students can be added to courses.",
                    error_code="INVALID_USER_ROLE",
                )

            course.students.add(student)
            return APIResponse.success(message="Student added to course successfully")
        return APIResponse.validation_error(serializer.errors)

    @extend_schema(
        summary="Remove Student from Course",
        description="Remove a student from a course (teachers only)",
        responses={
            200: CommonResponses.SUCCESS_RESPONSE,
            400: CommonResponses.VALIDATION_ERROR,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    )
    @action(
        detail=True, methods=["delete"], url_path="remove-student/(?P<user_id>[0-9]+)"
    )
    def remove_student(self, request, pk=None, user_id=None):
        course = self.get_object()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return APIResponse.error(
                message="User does not exist.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if user.role != user.Role.STUDENT:
            return APIResponse.error(
                message="Only students can be removed from courses.",
                error_code="INVALID_USER_ROLE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not course.students.filter(id=user.id).exists():
            return APIResponse.error(
                message="User is not enrolled in this course.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        course.students.remove(user)
        return APIResponse.success(message="Student removed from course successfully")

    @extend_schema(
        summary="Add Teacher to Course",
        description="Add a teacher to a course (course owner only)",
        request=CourseEnrollmentSerializer,
        responses={
            200: CommonResponses.SUCCESS_RESPONSE,
            400: CommonResponses.VALIDATION_ERROR,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["courses"],
    )
    @action(detail=True, methods=["post"], url_path="add-teacher")
    def add_teacher(self, request, pk=None):
        course = self.get_object()

        serializer = CourseEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.validated_data["user_id"]

            if teacher.role != teacher.Role.TEACHER:
                return APIResponse.error(
                    message="Only teachers can be added as course teachers.",
                    error_code="INVALID_USER_ROLE",
                )

            course.teachers.add(teacher)
            return APIResponse.success(message="Teacher added to course successfully")
        return APIResponse.validation_error(serializer.errors)

    @extend_schema(
        summary="Remove Teacher from Course",
        description="Remove a teacher from a course (course owner only)",
        responses={
            200: CommonResponses.SUCCESS_RESPONSE,
            400: CommonResponses.VALIDATION_ERROR,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    )
    @action(
        detail=True, methods=["delete"], url_path="remove-teacher/(?P<user_id>[0-9]+)"
    )
    def remove_teacher(self, request, pk=None, user_id=None):
        course = self.get_object()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return APIResponse.error(
                message="User does not exist.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if user.role != user.Role.TEACHER:
            return APIResponse.error(
                message="Only teachers can be removed from courses.",
                error_code="INVALID_USER_ROLE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not course.teachers.filter(id=user.id).exists():
            return APIResponse.error(
                message="User is not a teacher of this course.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent removing the course owner
        if user == course.teacher:
            return APIResponse.error(
                message="Cannot remove the course owner.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        course.teachers.remove(user)
        return APIResponse.success(message="Teacher removed from course successfully")

    @extend_schema(
        summary="List Course Lectures",
        description="Retrieve a list of lectures for a specific course",
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.ORDERING,
        ],
        responses={
            200: LectureListSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    )
    @action(detail=True, methods=["get"], url_path="lectures")
    def list_lectures(self, request, pk=None):
        course = self.get_object()

        if not course.can_access(request.user):
            return APIResponse.error(
                message="You don't have permission to access this course.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        lectures = Lecture.objects.filter(course=course).select_related("course")

        ordering = request.query_params.get("ordering", "created_at")
        if ordering:
            lectures = lectures.order_by(ordering)

        page = self.paginate_queryset(lectures)
        if page is not None:
            serializer = LectureListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = LectureListSerializer(lectures, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get Course Lecture",
        description="Retrieve a specific lecture from a course",
        responses={
            200: LectureDetailSerializer,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    )
    @action(detail=True, methods=["get"], url_path="lectures/(?P<lecture_id>[^/.]+)")
    def get_lecture(self, request, pk=None, lecture_id=None):
        course = self.get_object()

        try:
            lecture = Lecture.objects.select_related("course").get(
                id=lecture_id, course=course
            )
        except Lecture.DoesNotExist:
            return APIResponse.error(
                message="Lecture not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if not lecture.can_access(request.user):
            return APIResponse.error(
                message="You don't have permission to access this lecture.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = LectureDetailSerializer(lecture)
        return Response(serializer.data)

    @extend_schema(
        summary="Create Course Lecture",
        description="Create a new lecture for a course (teachers only)",
        request=LectureCreateSerializer,
        responses={
            201: LectureDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    )
    @action(detail=True, methods=["post"], url_path="lectures")
    def create_lecture(self, request, pk=None):
        course = self.get_object()

        if not course.is_teacher(request.user):
            return APIResponse.error(
                message="Only teachers can create lectures for this course.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = LectureCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            lecture = serializer.save(course=course)
            response_serializer = LectureDetailSerializer(lecture)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return APIResponse.validation_error(serializer.errors)

    @extend_schema(
        summary="Update Course Lecture",
        description="Update a specific lecture in a course (teachers only)",
        request=LectureUpdateSerializer,
        responses={
            200: LectureDetailSerializer,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    )
    @action(detail=True, methods=["put"], url_path="lectures/(?P<lecture_id>[^/.]+)")
    def update_lecture(self, request, pk=None, lecture_id=None):
        course = self.get_object()

        try:
            lecture = Lecture.objects.select_related("course").get(
                id=lecture_id, course=course
            )
        except Lecture.DoesNotExist:
            return APIResponse.error(
                message="Lecture not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if not course.is_teacher(request.user):
            return APIResponse.error(
                message="Only teachers can update lectures for this course.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = LectureUpdateSerializer(
            lecture, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            updated_lecture = serializer.save()
            response_serializer = LectureDetailSerializer(updated_lecture)
            return Response(response_serializer.data)

        return APIResponse.validation_error(serializer.errors)

    @extend_schema(
        summary="Delete Course Lecture",
        description="Delete a specific lecture from a course (teachers only)",
        responses={
            204: CommonResponses.SUCCESS_RESPONSE,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["lectures"],
    )
    @action(detail=True, methods=["delete"], url_path="lectures/(?P<lecture_id>[^/.]+)")
    def delete_lecture(self, request, pk=None, lecture_id=None):
        course = self.get_object()

        try:
            lecture = Lecture.objects.select_related("course").get(
                id=lecture_id, course=course
            )
        except Lecture.DoesNotExist:
            return APIResponse.error(
                message="Lecture not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if not course.is_teacher(request.user):
            return APIResponse.error(
                message="Only teachers can delete lectures for this course.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        lecture.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="List Available Courses",
        description="Paginated list of available courses for students.",
        responses={
            200: CourseListSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
        },
        tags=["courses"],
    )
    @action(detail=False, methods=["get"], url_path="available")
    def available_courses(self, request):
        user = request.user

        if not user.is_student:
            return APIResponse.error(
                message="Only students can view available courses.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        queryset = (
            Course.objects.select_related("teacher")
            .prefetch_related("teachers", "students")
            .filter(is_active=True)
            .exclude(students=user)  # Exclude courses already enrolled
            .annotate(
                _student_count=Count("students"), _teacher_count=Count("teachers")
            )
        )

        # Apply search filter
        search = request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search)
                | models.Q(description__icontains=search)
                | models.Q(teacher__first_name__icontains=search)
                | models.Q(teacher__last_name__icontains=search)
            )

        # Apply ordering
        ordering = request.query_params.get("ordering", "-created_at")
        if ordering:
            queryset = queryset.order_by(ordering)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CourseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CourseListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Enroll in Course",
        description="Enroll the current student in a course",
        responses={
            200: CommonResponses.SUCCESS_RESPONSE,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    )
    @action(detail=True, methods=["post"], url_path="enroll")
    def enroll_in_course(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if not user.is_student:
            return APIResponse.error(
                message="Only students can enroll in courses.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if not course.is_active:
            return APIResponse.error(
                message="This course is not available for enrollment.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if course.students.filter(id=user.id).exists():
            return APIResponse.error(
                message="You are already enrolled in this course.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course.add_student(user)
            return APIResponse.success(message="Successfully enrolled in the course")
        except ValidationError as e:
            return APIResponse.error(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Unenroll from Course",
        description="Unenroll the current student from a course",
        responses={
            200: CommonResponses.SUCCESS_RESPONSE,
            400: CommonResponses.VALIDATION_ERROR,
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    )
    @action(detail=True, methods=["post"], url_path="unenroll")
    def unenroll_from_course(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if not user.is_student:
            return APIResponse.error(
                message="Only students can unenroll from courses.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if not course.students.filter(id=user.id).exists():
            return APIResponse.error(
                message="You are not enrolled in this course.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        course.remove_student(user)
        return APIResponse.success(message="Successfully unenrolled from the course")

    @extend_schema(
        summary="List Students of a Course",
        description="Retrieve a paginated list of students enrolled in a specific course.",
        parameters=[
            CommonParameters.PAGE,
            CommonParameters.PAGE_SIZE,
            CommonParameters.ORDERING,
        ],
        responses={
            200: CourseStudentSerializer(many=True),
            401: CommonResponses.UNAUTHORIZED,
            403: CommonResponses.PERMISSION_DENIED,
            404: CommonResponses.NOT_FOUND,
        },
        tags=["courses"],
    )
    @action(detail=True, methods=["get"], url_path="students")
    def list_students(self, request, pk=None):
        course = self.get_object()

        if not course.is_teacher(request.user):
            return APIResponse.error(
                message="You don't have permission to view students of this course.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        students = course.students.all()

        ordering = request.query_params.get("ordering", "user__first_name")
        if ordering:
            students = students.order_by(ordering)

        page = self.paginate_queryset(students)
        if page is not None:
            serializer = CourseStudentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CourseStudentSerializer(students, many=True)
        return Response(serializer.data)
