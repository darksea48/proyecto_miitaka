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

class CocinaIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index_cocina.html'


# ============================================
# VISTAS PARA ITEMS
# ============================================

class ItemListView(LoginRequiredMixin, ListView):
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


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'detail_item.html'
    context_object_name = 'item'


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'form_item.html'
    success_url = reverse_lazy('listar_items')
    
    def get_initial(self):
        """Preseleccionar la categoría si viene en el parámetro GET"""
        initial = super().get_initial()
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            initial['categoria'] = categoria_id
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, 'Item creado exitosamente.')
        return super().form_valid(form)


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'form_item.html'
    success_url = reverse_lazy('listar_items')
    
    def form_valid(self, form):
        messages.success(self.request, 'Item actualizado exitosamente.')
        return super().form_valid(form)


@login_required
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Context in CategoriaItemListView:", context) # Debug print
        return context


class CategoriaItemCreateView(LoginRequiredMixin, CreateView):
    model = CategoriaItem
    form_class = CategoriaItemForm
    template_name = 'form_categoria.html'
    success_url = reverse_lazy('listar_categorias')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada exitosamente.')
        return super().form_valid(form)


class CategoriaItemUpdateView(LoginRequiredMixin, UpdateView):
    model = CategoriaItem
    form_class = CategoriaItemForm
    template_name = 'form_categoria.html'
    success_url = reverse_lazy('listar_categorias')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return super().form_valid(form)


@login_required
def categoria_delete(request, pk):
    # SELECT * FROM cocina_categoriaitem WHERE id = pk LIMIT 1
    categoria = get_object_or_404(CategoriaItem, pk=pk)
    # DELETE FROM cocina_categoriaitem WHERE id = pk
    categoria.delete()
    messages.success(request, 'Categoría eliminada exitosamente.')
    return redirect('listar_categorias')

@login_required
def agregar_item(request, categoria_pk):
    categoria = get_object_or_404(CategoriaItem, pk=categoria_pk)
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            nuevo_item = form.save(commit=False)
            nuevo_item.categoria = categoria
            nuevo_item.save()
            messages.success(request, 'Item agregado a la categoría exitosamente.')
            return redirect('listar_categorias')
    else:
        form = ItemForm(initial={'categoria': categoria})
        form.fields['categoria'].widget.attrs['disabled'] = True  # Hacer el campo de categoría de solo lectura
        form.fields['categoria'].required = False  # Evitar validación en el campo deshabilitado
    return render(request, 'form_item.html', {'form': form, 'categoria': categoria})