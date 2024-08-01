from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class RestrictLoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == reverse('login') and request.method == 'POST':
            username = request.POST.get('username')
            if username != 'munazza':
                return redirect('restrict_login_error')
