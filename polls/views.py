from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.forms import ModelForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Poll, Category, Tag, UserProfile, UserTagHistory


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


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)

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

        return render(request, 'polls/profile.html', context)
