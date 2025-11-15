from django.shortcuts import render, redirect
from django.views.generic import TemplateView

# Create your views here.

# ============================================
# VISTA PRINCIPAL
# ============================================

class IndexView(TemplateView):
    template_name = 'index.html'

def sitio_admin(request):
    return redirect('/admin/')
