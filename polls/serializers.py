from django.contrib.auth.models import Group
from django.db import models
from rest_framework import serializers

from .models import Tag, Poll, Choice, User


# class TagSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(max_length=100)
#
#     def create(self, validated_data):
#         return Tag.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.save()
#         return instance


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'role']

    def get_role(self, obj):
        if obj.user_type == 1:
            return "Regular"
        return "Admin"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text']


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Poll
        fields = ['id', 'title', 'question', 'category', 'tags', 'expiry_date', 'choices', 'created_by']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        tags_data = validated_data.pop('tags')
        try:
            poll = Poll.objects.create(**validated_data)
            poll.tags.set(tags_data)
            for choice_data in choices_data:
                Choice.objects.create(poll=poll, **choice_data)
            return poll
        except serializers.ValidationError as e:
            raise e

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', None)
        tags_data = validated_data.pop('tags', None)

        instance.title = validated_data.get('title', instance.title)
        instance.question = validated_data.get('question', instance.question)
        instance.expiry_date = validated_data.get('expiry_date', instance.expiry_date)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if choices_data is not None:
            # Update choices
            instance.choices.all().delete()
            for choice_data in choices_data:
                Choice.objects.create(poll=instance, **choice_data)

        return instance


# class ChoiceSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     poll = PollSerializer()
#     choice_text = serializers.CharField(max_length=200)
