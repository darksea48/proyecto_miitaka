from django.urls import path
from . import views

urlpatterns = [
    # Vista principal de cocina
    path('', views.CocinaIndexView.as_view(), name='cocina_index'),
    
    # URLs de Items
    path('items/', views.ItemListView.as_view(), name='listar_items'),
    path('items/crear/', views.ItemCreateView.as_view(), name='crear_item'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='ver_item'),
    path('items/<int:pk>/editar/', views.ItemUpdateView.as_view(), name='editar_item'),
    path('items/<int:pk>/eliminar/', views.item_delete, name='eliminar_item'),
    
    # URLs de Categorías
    path('categorias/', views.CategoriaItemListView.as_view(), name='listar_categorias'),
    path('categorias/crear/', views.CategoriaItemCreateView.as_view(), name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.CategoriaItemUpdateView.as_view(), name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='eliminar_categoria'),
]
