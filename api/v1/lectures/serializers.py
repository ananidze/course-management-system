from rest_framework import serializers
from lectures.models import Lecture


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = [
            "id",
            "course",
            "topic",
            "description",
            "presentation_file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LectureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = [
            "topic",
            "description",
            "presentation_file",
        ]

    def validate(self, attrs):
        return attrs


class LectureUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = [
            "topic",
            "description",
            "presentation_file",
        ]

    def validate(self, attrs):
        return attrs


class LectureDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = Lecture
        fields = [
            "id",
            "course",
            "course_id",
            "course_title",
            "topic",
            "description",
            "presentation_file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LectureListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = Lecture
        fields = [
            "id",
            "course_id",
            "course_title",
            "topic",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
