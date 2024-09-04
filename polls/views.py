import datetime

from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import Group
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import login, logout
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from django_site import settings
from .models import User, Poll, Choice, Category, Tag, UserProfile, UserTagHistory, UserPollHistory
from .serializers import (GroupSerializer, TagSerializer, PollSerializer, ChoiceSerializer,
                          CategorySerializer, UserLoginSerializer,
                          UserRegisterSerializer, UserProfileSerializer, ChangePasswordSerializer,
                          UserSelfUpdateSerializer, PasswordResetRequestSerializer, PasswordResetSerializer)
from .serializers import SingleUsePasswordResetTokenGenerator
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


def vote_view(request, poll_id):
    context = {
        "poll_id": poll_id
    }
    return render(request, 'polls/vote.html', context=context)


def poll_results_view(request):
    return render(request, 'polls/poll_results.html')


class LandingPageAPIView(APIView):
    permission_classes = []

    def get(self, request):
        login_url = reverse('user-login')
        signup_url = reverse('user-register')

        response = {
            "data": {
                "login_url": login_url,
                "signup_url": signup_url,
            }
        }

        return Response(response, status=status.HTTP_200_OK)


class UserLoginAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:

                login(request, user)  # Log the user in and set session data

                # Blacklist any existing refresh tokens for the user
                tokens = OutstandingToken.objects.filter(user=user)
                if tokens.exists():
                    for token in tokens:
                        _, _ = BlacklistedToken.objects.get_or_create(token=token)

                # Generate new refresh and access tokens
                refresh = RefreshToken.for_user(user)

                response = {
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
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
            login(request, user)  # Log the user in and set session data

            refresh = RefreshToken.for_user(user)

            response = {
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    def post(self, request, *args):
        try:
            # Handle session logout
            logout(request)

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


class ChangePasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            user = request.user
            logout(request)

            tokens = OutstandingToken.objects.filter(user=user)
            if tokens.exists():
                for token in tokens:
                    _, _ = BlacklistedToken.objects.get_or_create(token=token)

            response = {
                "detail": "Password updated successfully."
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    permission_classes = []

    password_reset_token = SingleUsePasswordResetTokenGenerator()

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            token = self.password_reset_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = request.build_absolute_uri(
                reverse('polls:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Send email
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            response = {
                "data": "Password reset link sent."
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(APIView):
    permission_classes = []

    def post(self, request, uidb64, token, *args, **kwargs):
        data = {
            **request.data,
            "uidb64": uidb64,
            "token": token
        }
        serializer = PasswordResetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": "Password has been reset."
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSelfUpdateAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSelfUpdateSerializer(user)
        response = {
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSelfUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupAPIView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            group = get_object_or_404(Group, pk=pk)
            serializer = GroupSerializer(group)
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            groups = Group.objects.all().order_by('name')
            serializer = GroupSerializer(groups, many=True)
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)


class PollAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def add_poll_to_results_page(self, poll):
        # add to poll results page
        channel_layer = get_channel_layer()
        poll_data = {
            'id': poll.id,
            'title': poll.title,
            'status': "Open",
            'question': poll.question,
            'choices': [
                {"id": choice.id, "choice_text": choice.choice_text, "votes": choice.votes}
                for choice in poll.choices.all()
            ],
            'top_choice': None
        }
        print(poll_data)
        try:
            async_to_sync(channel_layer.group_send)(
                'poll_results',
                {
                    'type': 'new_poll',
                    'poll_data': poll_data
                }
            )
        except Exception as e:
            print(f"Error sending message to group: {e}")

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            poll = get_object_or_404(Poll, pk=pk)
            serializer = PollSerializer(poll)
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            open_polls = Poll.objects.filter(expiry_date__gt=datetime.datetime.now())
            open_poll_ser = PollSerializer(open_polls, context={'short': True}, many=True)

            user = request.user

            try:
                user_tag_history = user.usertaghistory.tag_history
                sorted_tags = sorted(user_tag_history.items(), key=lambda x: x[1], reverse=True)[:5]
                top_tags = [tag_id for tag_id, count in sorted_tags]

            except UserTagHistory.DoesNotExist:
                top_tags = []

            voted_poll_ids = UserPollHistory.objects.filter(user=user).values_list('poll_id', flat=True)

            recommended_polls = Poll.objects.filter(
                Q(expiry_date__gt=datetime.datetime.now()) &
                Q(tags__in=top_tags)
            ).exclude(id__in=voted_poll_ids).distinct().order_by('expiry_date')[:5]

            rec_poll_ser = PollSerializer(recommended_polls, context={'short': True}, many=True)

            response = {
                "data": {
                    "recommendations": rec_poll_ser.data,
                    "open_polls": open_poll_ser.data
                }
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = PollSerializer(data=request.data, context={'request': request})
        user = request.user
        if serializer.is_valid():
            serializer.save(created_by=user)

            self.add_poll_to_results_page(serializer.instance)

            response = {
                "data": serializer.data
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
                "data": serializer.data
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
                "data": serializer.data
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
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            choices = Choice.objects.all()
            serializer = ChoiceSerializer(choices, many=True)
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ChoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        choice = get_object_or_404(Choice, pk=pk)
        serializer = ChoiceSerializer(choice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        choice = get_object_or_404(Choice, pk=pk)
        serializer = ChoiceSerializer(choice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
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
                "data": serializer.data
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
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

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

        choice.vote_count += 1
        choice.save()

        user = request.user
        UserPollHistory.objects.create(user=user, poll=poll, choice=choice)

        serializer = PollSerializer(poll, context={'short': True})
        response = {
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)


class PollResultsAPIView(APIView):
    permission_classes = []

    def get_poll_data(self, poll, voted):
        choices = poll.choices.all()
        top_choice = choices.order_by('-vote_count')[0]

        poll_status = "Open"
        if poll.expiry_date < timezone.now():
            poll_status = "Closed"

        poll_data = {
            "id": poll.id,
            "status": poll_status,
            "voted": voted,
            "title": poll.title,
            "question": poll.question,
            "choices": [
                {"id": choice.id, "choice_text": choice.choice_text, "votes": choice.votes}
                for choice in choices
            ],
            "top_choice": top_choice.choice_text if top_choice else None
        }

        return poll_data

    def get(self, request):
        user = request.user
        polls = Poll.objects.all().order_by('-expiry_date')
        user_polls_history = UserPollHistory.objects.filter(user=user, poll__in=polls)
        user_polls = sorted([history.poll for history in user_polls_history], key=lambda x: x.expiry_date, reverse=True)

        response = {"data": [self.get_poll_data(poll) for poll in user_polls]}

        for poll in polls:
            if poll in user_polls:
                continue
            response["data"].append(self.get_poll_data(poll))

        return Response(response, status=status.HTTP_200_OK)


class TagAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            tag = get_object_or_404(Tag, pk=pk)
            serializer = TagSerializer(tag)
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
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
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data
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
            "data": {
                'profile': profile_serializer.data,
                'last_voted_polls': polls_serializer.data,
                'top_tags': tags_serializer.data
            }
        }

        # Admin users additional data
        if profile.role == "Admin":
            created_polls = Poll.objects.filter(created_by=user)
            created_polls_ser = PollSerializer(created_polls, context={'short': True}, many=True)
            response["data"].update({
                'created_polls': created_polls_ser.data,
            })

        return Response(response, status=status.HTTP_200_OK)
