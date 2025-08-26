"""
Reusable OpenAPI documentation components for consistent API documentation.
"""

from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


# Common Response Examples
class CommonResponses:
    """Common response examples used across the API."""

    SUCCESS_RESPONSE = OpenApiResponse(
        description="Operation completed successfully",
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "success": True,
                    "message": "Operation completed successfully",
                    "data": None,
                },
            )
        ],
    )

    VALIDATION_ERROR = OpenApiResponse(
        description="Validation error",
        examples=[
            OpenApiExample(
                "Validation Error",
                value={
                    "success": False,
                    "message": "Validation failed",
                    "errors": {
                        "field_name": ["This field is required."],
                    },
                },
            )
        ],
    )

    NOT_FOUND = OpenApiResponse(
        description="Resource not found",
        examples=[
            OpenApiExample(
                "Not Found",
                value={
                    "success": False,
                    "message": "Resource not found",
                    "error_code": "NOT_FOUND",
                },
            )
        ],
    )

    PERMISSION_DENIED = OpenApiResponse(
        description="Permission denied",
        examples=[
            OpenApiExample(
                "Permission Denied",
                value={
                    "success": False,
                    "message": "You do not have permission to perform this action",
                    "error_code": "PERMISSION_DENIED",
                },
            )
        ],
    )

    UNAUTHORIZED = OpenApiResponse(
        description="Authentication required",
        examples=[
            OpenApiExample(
                "Unauthorized",
                value={
                    "success": False,
                    "message": "Authentication credentials were not provided",
                    "error_code": "UNAUTHORIZED",
                },
            )
        ],
    )


# Common Parameters
class CommonParameters:
    """Common parameters used across the API."""

    PAGE = OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Page number for pagination",
        default=1,
    )

    PAGE_SIZE = OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Number of items per page",
        default=10,
    )

    SEARCH = OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Search term for filtering results",
    )

    ORDERING = OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Order results by field (prefix with - for descending)",
    )


# Authentication Responses
class AuthResponses:
    """Authentication-specific response examples."""

    LOGIN_SUCCESS = OpenApiResponse(
        description="Login successful",
        examples=[
            OpenApiExample(
                "Login Success",
                value={
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "tokens": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        },
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "student",
                        },
                    },
                },
            )
        ],
    )

    REGISTRATION_SUCCESS = OpenApiResponse(
        description="User registered successfully",
        examples=[
            OpenApiExample(
                "Registration Success",
                value={
                    "success": True,
                    "message": "User registered successfully",
                    "data": {
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "student",
                        },
                    },
                },
            )
        ],
    )


# Course Responses
class CourseResponses:
    """Course-specific response examples."""

    COURSE_CREATED = OpenApiResponse(
        description="Course created successfully",
        examples=[
            OpenApiExample(
                "Course Created",
                value={
                    "success": True,
                    "message": "Course created successfully",
                    "data": {
                        "id": 1,
                        "title": "Introduction to Python",
                        "description": "Learn Python programming basics",
                        "teacher": {
                            "id": 1,
                            "email": "teacher@example.com",
                            "first_name": "Jane",
                            "last_name": "Smith",
                        },
                        "students": [],
                        "teachers": [],
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                },
            )
        ],
    )

    COURSE_LIST = OpenApiResponse(
        description="List of courses retrieved successfully",
        examples=[
            OpenApiExample(
                "Course List",
                value={
                    "success": True,
                    "message": "Courses retrieved successfully",
                    "data": {
                        "count": 2,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "title": "Introduction to Python",
                                "description": "Learn Python programming basics",
                                "teacher": {
                                    "id": 1,
                                    "email": "teacher@example.com",
                                    "first_name": "Jane",
                                    "last_name": "Smith",
                                },
                            },
                            {
                                "id": 2,
                                "title": "Advanced Django",
                                "description": "Master Django web development",
                                "teacher": {
                                    "id": 2,
                                    "email": "teacher2@example.com",
                                    "first_name": "Bob",
                                    "last_name": "Johnson",
                                },
                            },
                        ],
                    },
                },
            )
        ],
    )


# Lecture Responses
class LectureResponses:
    """Lecture-specific response examples."""

    LECTURE_CREATED = OpenApiResponse(
        description="Lecture created successfully",
        examples=[
            OpenApiExample(
                "Lecture Created",
                value={
                    "success": True,
                    "message": "Lecture created successfully",
                    "data": {
                        "id": 1,
                        "topic": "Python Basics",
                        "presentation_file": "http://localhost:8000/media/presentations/python_basics.pdf",
                        "course": 1,
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                },
            )
        ],
    )

    LECTURE_LIST = OpenApiResponse(
        description="List of lectures retrieved successfully",
        examples=[
            OpenApiExample(
                "Lecture List",
                value={
                    "success": True,
                    "message": "Lectures retrieved successfully",
                    "data": {
                        "count": 2,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "topic": "Python Basics",
                                "presentation_file": "http://localhost:8000/media/presentations/python_basics.pdf",
                                "course": 1,
                                "created_at": "2024-01-01T00:00:00Z",
                            },
                            {
                                "id": 2,
                                "topic": "Django Fundamentals",
                                "presentation_file": "http://localhost:8000/media/presentations/django_fundamentals.pdf",
                                "course": 1,
                                "created_at": "2024-01-02T00:00:00Z",
                            },
                        ],
                    },
                },
            )
        ],
    )


# Homework Responses
class HomeworkResponses:
    """Homework-specific response examples."""

    HOMEWORK_CREATED = OpenApiResponse(
        description="Homework created successfully",
        examples=[
            OpenApiExample(
                "Homework Created",
                value={
                    "success": True,
                    "message": "Homework created successfully",
                    "data": {
                        "id": 1,
                        "title": "Python Variables Assignment",
                        "description": "Create variables and perform basic operations",
                        "lecture": 1,
                        "due_date": "2024-01-15T23:59:59Z",
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                },
            )
        ],
    )

    HOMEWORK_LIST = OpenApiResponse(
        description="List of homework retrieved successfully",
        examples=[
            OpenApiExample(
                "Homework List",
                value={
                    "success": True,
                    "message": "Homework list retrieved successfully",
                    "data": {
                        "count": 2,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "title": "Python Variables Assignment",
                                "description": "Create variables and perform basic operations",
                                "lecture": 1,
                                "due_date": "2024-01-15T23:59:59Z",
                                "created_at": "2024-01-01T00:00:00Z",
                            },
                            {
                                "id": 2,
                                "title": "Django Models Exercise",
                                "description": "Create Django models and migrations",
                                "lecture": 2,
                                "due_date": "2024-01-20T23:59:59Z",
                                "created_at": "2024-01-02T00:00:00Z",
                            },
                        ],
                    },
                },
            )
        ],
    )

    SUBMISSION_CREATED = OpenApiResponse(
        description="Homework submitted successfully",
        examples=[
            OpenApiExample(
                "Submission Created",
                value={
                    "success": True,
                    "message": "Homework submitted successfully",
                    "data": {
                        "id": 1,
                        "content": "My homework solution...",
                        "homework": 1,
                        "student": 1,
                        "submitted_at": "2024-01-10T12:00:00Z",
                    },
                },
            )
        ],
    )


# Submission Responses
class SubmissionResponses:
    """Submission-specific response examples."""

    SUBMISSION_LIST = OpenApiResponse(
        description="List of submissions retrieved successfully",
        examples=[
            OpenApiExample(
                "Submissions List",
                value={
                    "success": True,
                    "message": "Submissions list retrieved successfully",
                    "data": {
                        "count": 2,
                        "next": None,
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "content": "My homework solution...",
                                "homework": {
                                    "id": 1,
                                    "title": "Python Variables Assignment",
                                },
                                "student": {
                                    "id": 1,
                                    "email": "student@example.com",
                                    "first_name": "John",
                                    "last_name": "Doe",
                                },
                                "submitted_at": "2024-01-10T12:00:00Z",
                                "grade": None,
                            },
                            {
                                "id": 2,
                                "content": "Another solution...",
                                "homework": {
                                    "id": 1,
                                    "title": "Python Variables Assignment",
                                },
                                "student": {
                                    "id": 2,
                                    "email": "student2@example.com",
                                    "first_name": "Jane",
                                    "last_name": "Smith",
                                },
                                "submitted_at": "2024-01-11T14:30:00Z",
                                "grade": {
                                    "id": 1,
                                    "grade": 85,
                                    "comments": "Good work!",
                                },
                            },
                        ],
                    },
                },
            )
        ],
    )


# Decorator Functions
def standard_responses(*status_codes):
    """Decorator to add standard responses to API endpoints."""
    responses = {}

    for status_code in status_codes:
        if status_code == 200:
            responses[200] = CommonResponses.SUCCESS_RESPONSE
        elif status_code == 201:
            responses[201] = CommonResponses.SUCCESS_RESPONSE
        elif status_code == 400:
            responses[400] = CommonResponses.VALIDATION_ERROR
        elif status_code == 401:
            responses[401] = CommonResponses.UNAUTHORIZED
        elif status_code == 403:
            responses[403] = CommonResponses.PERMISSION_DENIED
        elif status_code == 404:
            responses[404] = CommonResponses.NOT_FOUND

    return responses


def paginated_response(serializer_class, description="List retrieved successfully"):
    """Create a paginated response for list endpoints."""
    return OpenApiResponse(
        description=description,
        examples=[
            OpenApiExample(
                "Paginated Response",
                value={
                    "success": True,
                    "message": description,
                    "data": {
                        "count": 10,
                        "next": "http://localhost:8000/api/v1/endpoint/?page=2",
                        "previous": None,
                        "results": [
                            # This will be populated by the serializer
                        ],
                    },
                },
            )
        ],
    )
