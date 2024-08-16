import datetime

from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import User, Poll, Choice, Category, Tag, UserProfile, UserTagHistory, UserPollHistory
from .serializers import (GroupSerializer, TagSerializer, PollSerializer, ChoiceSerializer,
                          CategorySerializer, UserSerializer, UserLoginSerializer,
                          UserRegisterSerializer, UserProfileSerializer)
from .permissions import IsSuperuser, IsSuperuserOrReadOnly, IsAdminOrReadOnly, IsOwnerOrReadOnly


class UserLoginAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Blacklist any existing refresh tokens for the user
                tokens = OutstandingToken.objects.filter(user=user)
                if tokens.exists():
                    for token in tokens:
                        _, _ = BlacklistedToken.objects.get_or_create(token=token)

                # Generate new refresh and access tokens
                refresh = RefreshToken.for_user(user)

                response = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "detail": "Invalid credentials, please try again."
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            response = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    def post(self, request, *args):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = {
                "detail": "Logged out!"
            }
            return Response(response, status=status.HTTP_200_OK)
        except KeyError:
            response = {
                "detail": "Refresh token not provided."
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except TokenError as e:
            response = {
                "detail": f"Token error: {str(e)}"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = {
                "detail": f"Logout failed!: {str(e)}"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperuser]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(user)
            response = {
                "user": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            response = {
                "users": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "user": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "user": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "user": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsSuperuserOrReadOnly]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            group = get_object_or_404(Group, pk=pk)
            serializer = GroupSerializer(group)
            response = {
                "group": serializer.data
            }
            return Response(group, status=status.HTTP_200_OK)
        else:
            groups = Group.objects.all().order_by('name')
            serializer = GroupSerializer(groups, many=True)
            response = {
                "groups": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "group": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        group = get_object_or_404(Group, pk=pk)
        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "group": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        group = get_object_or_404(Group, pk=pk)
        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "group": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        group = get_object_or_404(Group, pk=pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PollAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            poll = get_object_or_404(Poll, pk=pk)
            serializer = PollSerializer(poll)
            response = {
                "poll": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            open_polls = Poll.objects.filter(expiry_date__gt=datetime.datetime.now())
            open_poll_ser = PollSerializer(open_polls, context={'short': True}, many=True)

            try:
                user = request.user
                user_tag_history = user.usertaghistory.tag_history
                sorted_tags = sorted(user_tag_history.items(), key=lambda x: x[1], reverse=True)[:5]
                top_tags = [tag_id for tag_id, count in sorted_tags]

            except UserTagHistory.DoesNotExist:
                top_tags = []

            recommended_polls = (Poll.objects.
                                 filter(Q(expiry_date__gt=datetime.datetime.now()) & Q(tags__in=top_tags)).
                                 order_by('expiry_date'))[:5]
            rec_poll_ser = PollSerializer(recommended_polls, context={'short': True}, many=True)

            response = {
                "recommendations": rec_poll_ser.data,
                "open_polls": open_poll_ser.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = PollSerializer(data=request.data, context={'request': request})
        user = request.user
        if serializer.is_valid():
            serializer.save(created_by=user)
            response = {
                "poll": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        poll = get_object_or_404(Poll, pk=pk)

        if poll.expiry_date < timezone.now():
            response = {
                "detail": "Closed poll cannot be updated!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = PollSerializer(poll, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            response = {
                "poll": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        poll = get_object_or_404(Poll, pk=pk)

        if poll.expiry_date < timezone.now():
            response = {
                "detail": "Closed poll cannot be updated!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = PollSerializer(poll, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "poll": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        poll = get_object_or_404(Poll, pk=pk)
        poll.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChoiceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            choice = get_object_or_404(Choice, pk=pk)
            serializer = ChoiceSerializer(choice)
            response = {
                "choice": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            choices = Choice.objects.all()
            serializer = ChoiceSerializer(choices, many=True)
            response = {
                "choices": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ChoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "choice": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        choice = get_object_or_404(Choice, pk=pk)
        serializer = ChoiceSerializer(choice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "choice": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        choice = get_object_or_404(Choice, pk=pk)
        serializer = ChoiceSerializer(choice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "choice": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        choice = get_object_or_404(Choice, pk=pk)
        choice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VoteAPIView(APIView):

    def get(self, request, poll_id, *args, **kwargs):
        try:
            poll = Poll.objects.get(pk=poll_id)
            serializer = PollSerializer(poll, context={'short': True})
            response = {
                "poll": serializer.data
            }
            if poll.expiry_date < timezone.now():
                response.update({"status": "Closed"})
            return Response(response, status=status.HTTP_200_OK)
        except Poll.DoesNotExist:
            response = {
                "detail": "Poll not found!"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, poll_id, *args, **kwargs):
        try:
            poll = Poll.objects.get(pk=poll_id)
            if poll.expiry_date < timezone.now():
                response = {
                    "detail": "Poll is closed!"
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Poll.DoesNotExist:
            response = {
                "detail": "Poll not found!"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        if request.user.userpollhistory_set.filter(poll_id=poll_id).exists():
            response = {
                "detail": "You have already voted!"
            }
            return Response(response, status=status.HTTP_200_OK)

        choice_id = request.data.get('choice_id')
        if choice_id is None:
            response = {
                "detail": "Choice id missing in request."
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            choice = Choice.objects.get(pk=choice_id, poll=poll)
        except Choice.DoesNotExist:
            response = {
                "detail": "Invalid choice!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        choice.votes += 1
        choice.save()

        user = request.user
        UserPollHistory.objects.create(user=user, poll=poll, choice=choice)

        serializer = PollSerializer(poll, context={'short': True})
        response = {
            "poll": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)


class PollResultsAPIView(APIView):
    permission_classes = []

    def get_poll_data(self, poll):
        choices = poll.choices.all()
        top_choice = choices.order_by('-votes')[0]

        poll_data = {
            "title": poll.title,
            "questions": poll.question,
            "choices": [
                {"choice text": choice.choice_text, "votes": choice.votes}
                for choice in choices
            ],
            "top choice": top_choice.choice_text if top_choice else None
        }

        return poll_data

    def get(self, request):
        user = request.user
        polls = Poll.objects.filter(expiry_date__lte=datetime.datetime.now()).order_by('-expiry_date')
        user_polls_history = UserPollHistory.objects.filter(user=user, poll__in=polls)
        user_polls = sorted([history.poll for history in user_polls_history], key=lambda x: x.expiry_date, reverse=True)

        response = [self.get_poll_data(poll) for poll in user_polls]

        for poll in polls:
            if poll in user_polls:
                continue
            response.append(self.get_poll_data(poll))

        return Response(response, status=status.HTTP_200_OK)


class TagAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            tag = get_object_or_404(Tag, pk=pk)
            serializer = TagSerializer(tag)
            response = {
                "tag": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            response = {
                "tags": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "tag": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "tag": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "tag": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            category = get_object_or_404(Category, pk=pk)
            serializer = CategorySerializer(category)
            response = {
                "category": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            response = {
                "categories": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "category": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "category": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "category": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)

        # Recent Polls user has voted in
        user_poll_history = user.userpollhistory_set.all().order_by('-voting_time')[:5]
        last_voted_polls = [history.poll for history in user_poll_history]

        # Top 5 tags
        try:
            user_tag_history = user.usertaghistory.tag_history
            sorted_tags = sorted(user_tag_history.items(), key=lambda x: x[1], reverse=True)[:5]
            top_tags = [Tag.objects.get(id=tag_id) for tag_id, count in sorted_tags]

        except UserTagHistory.DoesNotExist:
            top_tags = []

        profile_serializer = UserProfileSerializer(profile)
        polls_serializer = PollSerializer(last_voted_polls, context={'short': True}, many=True)
        tags_serializer = TagSerializer(top_tags, many=True)

        response = {
            'profile': profile_serializer.data,
            'last_voted_polls': polls_serializer.data,
            'top_tags': tags_serializer.data
        }

        # Admin users additional data
        if profile.role == "Admin":
            created_polls = Poll.objects.filter(created_by=user)
            created_polls_ser = PollSerializer(created_polls, context={'short': True}, many=True)
            response.update({
                'created_polls': created_polls_ser.data,
            })

        return Response(response, status=status.HTTP_200_OK)
