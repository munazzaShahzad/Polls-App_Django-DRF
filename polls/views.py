from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.forms import ModelForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
# from rest_framework.decorators import api_view

from .serializers import (GroupSerializer, TagSerializer, PollSerializer, ChoiceSerializer,
                          UserSerializer, UserLoginSerializer, UserRegisterSerializer)
from .models import User, Poll, Choice, Category, Tag, UserProfile, UserTagHistory


class UserLoginAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/login.html')

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                response = {
                    'success': True,
                    'username': user.username,
                    'email': user.email,
                    'token': token.key
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "detail": "Invalid credentials, please try again."
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                'success': True,
                'user': serializer.data,
                'token': Token.objects.get(user=User.objects.get(username=serializer.data['username'])).key
            }
            return Response(response, status=status.HTTP_200_OK)
        raise ValidationError(serializer.errors, code=status.HTTP_406_NOT_ACCEPTABLE)


class UserLogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        return render(request, 'registration/logout.html')

    def post(self, request, *args):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"success": True, "detail": "Logged out!"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"success": False, "detail": "Token not found!"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Polls to be viewed or edited.
    """
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class PollViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Polls to be viewed or edited.
    """
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# poll form
class PollForm(ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'question', 'expiry_date', 'category', 'tags', 'created_by']


class PollListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        polls = Poll.objects.all()
        return render(request, 'polls/poll_list.html', {'polls': polls})


@method_decorator(csrf_exempt, name='dispatch')
class PollDetailView(View):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            poll = get_object_or_404(Poll, pk=pk)
            return render(request, 'polls/poll_detail.html', {'poll': poll})
        else:
            form = PollForm()
            return render(request, 'polls/poll_form.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = PollForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('polls:poll_list')
        return render(request, 'polls/poll_form.html', {'form': form})

    def put(self, request, pk, *args, **kwargs):
        poll = get_object_or_404(Poll, pk=pk)
        form = PollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            return redirect('polls:poll_detail', pk=poll.pk)
        return render(request, 'polls/poll_form.html', {'form': form})

    def patch(self, request, pk, *args, **kwargs):
        poll = get_object_or_404(Poll, pk=pk)
        form = PollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            return redirect('polls:poll_detail', pk=poll.pk)
        return render(request, 'polls/poll_form.html', {'form': form})

    def delete(self, request, pk, *args, **kwargs):
        poll = get_object_or_404(Poll, pk=pk)
        poll.delete()
        return redirect('polls:poll_list')


# class ProfileView(LoginRequiredMixin, View):
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)

        # Recent Polls user has voted in
        user_poll_history = user.userpollhistory_set.all().order_by('-voting_time')[:5]
        voted_poll_ids = [history.poll.id for history in user_poll_history]
        last_voted_polls = Poll.objects.filter(id__in=voted_poll_ids)

        # Top 5 tags
        try:
            user_tag_history = user.usertaghistory.tag_history
            sorted_tags = sorted(user_tag_history.items(), key=lambda x: x[1], reverse=True)[:5]
            top_tags = [Tag.objects.get(id=tag_id) for tag_id, count in sorted_tags]

        except UserTagHistory.DoesNotExist:
            top_tags = []

        context = {
            'profile': profile,
            'last_voted_polls': last_voted_polls,
            'top_tags': top_tags
        }

        # Admin users additional options
        if profile.role == "Admin":
            created_polls = Poll.objects.filter(created_by=user)
            categories = Category.objects.all()
            tags = Tag.objects.all()
            context.update({
                'created_polls': created_polls,
                'categories': categories,
                'tags': tags,
            })

        # return render(request, 'polls/profile.html', context)
        return Response(context)

# # tag view functions (with serializer)
#
# @api_view(['GET', 'POST'])
# def tag_list(request):
#     """
#     Display list of tags, or create a new tag
#     """
#     if request.method == 'GET':
#         tags = Tag.objects.all().order_by('name')
#         ser = TagSerializer(tags, many=True)
#         return Response(ser.data)
#     elif request.method == 'POST':
#         ser = TagSerializer(data=request.data)
#         if ser.is_valid():
#             ser.save()
#             return Response(ser.data, status=status.HTTP_201_CREATED)
#         return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def tag_detail(request, pk):
#     """
#     Retrieve, Update or Delete a Tag
#     """
#     try:
#         tag = Tag.objects.get(pk=pk)
#     except Tag.DoesNotExist:
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#
#     if request.method == 'GET':
#         ser = TagSerializer(tag)
#         return Response(ser.data)
#     elif request.method == 'PUT':
#         ser = TagSerializer(tag, data=request.data)
#         if ser.is_valid():
#             ser.save()
#             return Response(ser.data)
#         return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'DELETE':
#         tag.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
