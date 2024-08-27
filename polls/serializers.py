from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Tag, Poll, Choice, User, UserProfile, Category


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'role']


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
        return user


class UserSelfUpdateSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_role(self, obj):
        if obj.user_type == 1:
            return "Regular"
        return "Admin"


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        user = self.context['request'].user
        if not check_password(data['old_password'], user.password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match."})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, data):
        password_reset_token = PasswordResetTokenGenerator()

        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})

        try:
            uid = urlsafe_base64_decode(data['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid token."})

        if not password_reset_token.check_token(user, data['token']):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password1'])
        user.save()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'vote_count']
        read_only_fields = ['vote_count']


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'question', 'category', 'tags', 'expiry_date', 'choices', 'created_by']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Customize the fields for vote API
        if self.context.get('short', False):
            fields = ['id', 'title', 'question', 'choices']
            representation = {field: representation[field] for field in fields}
        return representation

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        tags_data = validated_data.pop('tags')

        if not choices_data or len(choices_data) < 1:
            raise serializers.ValidationError("At least one choice is required.")

        # Create Poll instance
        poll = Poll.objects.create(**validated_data)

        # Handle linking existing tags
        if tags_data is not None:
            poll.tags.set(tags_data)

        # Create Choice instances
        for choice_data in choices_data:
            Choice.objects.create(poll=poll, **choice_data)

        return poll

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', None)
        tags_data = validated_data.pop('tags', None)

        # Update Poll fields
        instance.title = validated_data.get('title', instance.title)
        instance.question = validated_data.get('question', instance.question)
        instance.expiry_date = validated_data.get('expiry_date', instance.expiry_date)
        instance.category = validated_data.get('category', instance.category)
        instance.save()

        # Update tags
        if tags_data is not None:
            instance.tags.set(tags_data)

        # Update choices
        if choices_data is not None:
            if len(choices_data) < 1:
                raise serializers.ValidationError("At least one choice is required.")

            # Get the current choices in order
            existing_choices = list(instance.choices.all())

            # Handle case where some choices were removed
            if len(choices_data) < len(existing_choices):
                raise serializers.ValidationError("Cannot remove choice from here!")

            # Iterate over both the existing choices and the incoming choices
            for choice_instance, choice_data in zip(existing_choices, choices_data):
                new_text = choice_data.get('choice_text')
                if choice_instance.choice_text != new_text:
                    choice_instance.choice_text = new_text
                    choice_instance.save()

            # Handle case where more choices were added in the update
            if len(choices_data) > len(existing_choices):
                for i in range(len(existing_choices), len(choices_data)):
                    Choice.objects.create(poll=instance, **choices_data[i])

        return instance
