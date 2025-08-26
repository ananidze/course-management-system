from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from homework.models import Homework, HomeworkSubmission, Grade
from users.models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role"]


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = [
            "id",
            "lecture",
            "title",
            "description",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HomeworkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = [
            "lecture",
            "title",
            "description",
            "due_date",
        ]

    def validate_lecture(self, value):
        user = self.context["request"].user
        course = value.course
        if not (user == course.teacher or user in course.teachers.all()):
            raise serializers.ValidationError(
                "You can only create homework for lectures in courses you teach."
            )
        return value


class HomeworkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = [
            "title",
            "description",
            "due_date",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        course = self.instance.lecture.course
        if not (user == course.teacher or user in course.teachers.all()):
            raise serializers.ValidationError(
                "You can only update homework for lectures in courses you teach."
            )
        return attrs


class HomeworkDetailSerializer(serializers.ModelSerializer):
    lecture_topic = serializers.CharField(source="lecture.topic", read_only=True)
    lecture_id = serializers.IntegerField(source="lecture.id", read_only=True)
    course_title = serializers.CharField(source="lecture.course.title", read_only=True)
    course_id = serializers.IntegerField(source="lecture.course.id", read_only=True)
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = [
            "id",
            "lecture",
            "lecture_id",
            "lecture_topic",
            "course_id",
            "course_title",
            "title",
            "description",
            "due_date",
            "submission_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(serializers.IntegerField())
    def get_submission_count(self, obj):
        return obj.submissions.count()


class HomeworkListSerializer(serializers.ModelSerializer):
    lecture_topic = serializers.CharField(source="lecture.topic", read_only=True)
    course_title = serializers.CharField(source="lecture.course.title", read_only=True)
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = [
            "id",
            "lecture_topic",
            "course_title",
            "title",
            "description",
            "due_date",
            "submission_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    @extend_schema_field(serializers.IntegerField())
    def get_submission_count(self, obj):
        return obj.submissions.count()


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = [
            "id",
            "homework",
            "student",
            "content",
            "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]


class HomeworkSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = [
            "content",
        ]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class HomeworkSubmissionDetailSerializer(serializers.ModelSerializer):
    student = UserMinimalSerializer(read_only=True)
    homework_title = serializers.CharField(source="homework.title", read_only=True)
    course_title = serializers.CharField(
        source="homework.lecture.course.title", read_only=True
    )
    grade = serializers.SerializerMethodField()

    class Meta:
        model = HomeworkSubmission
        fields = [
            "id",
            "homework",
            "homework_title",
            "course_title",
            "student",
            "content",
            "submitted_at",
            "grade",
        ]
        read_only_fields = ["id", "submitted_at"]

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_grade(self, obj):
        try:
            grade = obj.grade
            return {
                "grade": grade.grade,
                "comments": grade.comments,
                "graded_by": UserMinimalSerializer(grade.graded_by).data,
                "graded_at": grade.graded_at,
            }
        except Grade.DoesNotExist:
            return None


class GradeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = [
            "grade",
            "comments",
        ]

    def create(self, validated_data):
        validated_data["graded_by"] = self.context["request"].user
        return super().create(validated_data)


class GradeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = [
            "grade",
            "comments",
        ]
