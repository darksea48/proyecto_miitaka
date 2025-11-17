from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.

# ============================================
# VISTA PRINCIPAL
# ============================================

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

@login_required
def sitio_admin(request):
    return redirect(reverse('admin:index'))

def handler404(request, exception):
    return render(request, 'error_404.html', status=404)
