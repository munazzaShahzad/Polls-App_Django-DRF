from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.forms import ModelForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Poll


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


def restrict_login_error_view(request):
    return render(request, 'registration/restrict_login_error.html')
