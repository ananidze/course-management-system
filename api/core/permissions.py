from rest_framework.permissions import BasePermission
from users.models import User


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT


class IsCourseTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER

    def has_object_permission(self, request, view, obj):
        return request.user == obj.teacher or request.user in obj.teachers.all()


class IsCourseOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER

    def has_object_permission(self, request, view, obj):
        return request.user == obj.teacher


class IsCourseStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT

    def has_object_permission(self, request, view, obj):
        return request.user in obj.students.filter(role=User.Role.STUDENT)


class IsLectureTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER

    def has_object_permission(self, request, view, obj):
        course = obj.course
        return request.user == course.teacher or request.user in course.teachers.all()


class IsHomeworkTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER

    def has_object_permission(self, request, view, obj):
        course = obj.lecture.course
        return request.user == course.teacher or request.user in course.teachers.all()


class IsHomeworkStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT

    def has_object_permission(self, request, view, obj):
        return request.user in obj.lecture.course.students.all()


class IsSubmissionOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT

    def has_object_permission(self, request, view, obj):
        return request.user == obj.student
