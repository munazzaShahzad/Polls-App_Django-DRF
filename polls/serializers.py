from django.contrib.auth.models import Group
from django.db import models
from rest_framework import serializers

from .models import Tag, Poll, Choice


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

    class Meta:
        model = Poll
        fields = ['id', 'title', 'question', 'expiry_date', 'choices']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        poll = Poll.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(poll=poll, **choice_data)
        return poll

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices')
        choices = instance.choices

        instance.title = validated_data.get('title', instance.title)
        instance.question = validated_data.get('question', instance.question)
        instance.expiry_date = validated_data.get('expiry_date', instance.expiry_date)
        instance.save()

        # for (choice_data, choice) in (choices_data, choices):
        #     choice.choice_text = choices_data.get('choice_text', choice.choice_text)


# class ChoiceSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     poll = PollSerializer()
#     choice_text = serializers.CharField(max_length=200)
