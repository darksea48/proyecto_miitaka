from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import CategoriaItem, Item
from .forms import CategoriaItemForm, ItemForm

# Create your views here.

# ============================================
# VISTA PRINCIPAL DE COCINA
# ============================================

class CocinaIndexView(TemplateView):
    template_name = 'index_cocina.html'


# ============================================
# VISTAS PARA ITEMS
# ============================================

class ItemListView(ListView):
    model = Item
    template_name = 'list_items.html'
    context_object_name = 'items'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Menú - Items'
        context['tipo_vista'] = 'items'
        context['url_crear'] = reverse_lazy('crear_item')
        context['texto_boton_crear'] = 'Nuevo Item'
        return context
    
    def get_queryset(self):
        # SELECT * FROM cocina_item ORDER BY nombre
        # TODO: Optimizar con select_related('categoria')
        queryset = super().get_queryset()
        categoria = self.request.GET.get('categoria')
        disponible = self.request.GET.get('disponible')
        
        if categoria:
            # SELECT * FROM cocina_item WHERE categoria_id = %s ORDER BY nombre
            queryset = queryset.filter(categoria_id=categoria)
        if disponible:
            # SELECT * FROM cocina_item WHERE disponible = %s ORDER BY nombre
            queryset = queryset.filter(disponible=(disponible == 'true'))
        
        return queryset


class ItemDetailView(DetailView):
    model = Item
    template_name = 'detail_item.html'
    context_object_name = 'item'


class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'form_item.html'
    success_url = reverse_lazy('listar_items')
    
    def form_valid(self, form):
        messages.success(self.request, 'Item creado exitosamente.')
        return super().form_valid(form)


class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'form_item.html'
    success_url = reverse_lazy('listar_items')
    
    def form_valid(self, form):
        messages.success(self.request, 'Item actualizado exitosamente.')
        return super().form_valid(form)


def item_delete(request, pk):
    # SELECT * FROM cocina_item WHERE id = pk LIMIT 1
    item = get_object_or_404(Item, pk=pk)
    # DELETE FROM cocina_item WHERE id = pk
    item.delete()
    messages.success(request, 'Item eliminado exitosamente.')
    return redirect('listar_items')


# ============================================
# VISTAS PARA CATEGORÍAS DE ITEMS
# ============================================

class CategoriaItemListView(ListView):
    model = CategoriaItem
    template_name = 'list_categorias.html'
    context_object_name = 'categorias'


class CategoriaItemCreateView(CreateView):
    model = CategoriaItem
    form_class = CategoriaItemForm
    template_name = 'form_categoria.html'
    success_url = reverse_lazy('listar_categorias')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada exitosamente.')
        return super().form_valid(form)


class CategoriaItemUpdateView(UpdateView):
    model = CategoriaItem
    form_class = CategoriaItemForm
    template_name = 'form_categoria.html'
    success_url = reverse_lazy('listar_categorias')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return super().form_valid(form)


def categoria_delete(request, pk):
    # SELECT * FROM cocina_categoriaitem WHERE id = pk LIMIT 1
    categoria = get_object_or_404(CategoriaItem, pk=pk)
    # DELETE FROM cocina_categoriaitem WHERE id = pk
    categoria.delete()
    messages.success(request, 'Categoría eliminada exitosamente.')
    return redirect('listar_categorias')
