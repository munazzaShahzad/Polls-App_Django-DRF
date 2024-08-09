from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from .models import Tag, Poll, Choice, User


class UserLoginSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ["id", "username", "password"]


class UserRegisterSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ["id", "username", "first_name",
                  "last_name", "email", "password", "confirm_password"]

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            detail = {
                "detail": "Username already exists!"
            }
            raise ValidationError(detail=detail)
        return username

    def validate(self, instance):
        if instance['password'] != instance['confirm_password']:
            raise ValidationError({"message": "Password mismatch!"})

        if User.objects.filter(email=instance['email']).exists():
            raise ValidationError({"message": "Account for this email already exists!"})

        return instance

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        Token.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'user_type', 'role']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).update(instance, validated_data)

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
