from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import CategoriaItem, Item
from .forms import CategoriaItemForm, ItemForm


# ============================================
# TESTS DE MODELOS
# ============================================

class CategoriaItemModelTest(TestCase):
    """Tests para el modelo CategoriaItem"""
    
    def setUp(self):
        """Configuración inicial"""
        self.categoria = CategoriaItem.objects.create(
            nombre='Entradas',
            descripcion='Platos de entrada y aperitivos'
        )
    
    def test_crear_categoria(self):
        """Test: Crear una categoría correctamente"""
        self.assertEqual(self.categoria.nombre, 'Entradas')
        self.assertEqual(self.categoria.descripcion, 'Platos de entrada y aperitivos')
    
    def test_str_categoria(self):
        """Test: Representación en string de la categoría"""
        self.assertEqual(str(self.categoria), 'Entradas')
    
    def test_categoria_sin_descripcion(self):
        """Test: Categoría puede crearse sin descripción"""
        categoria = CategoriaItem.objects.create(nombre='Postres')
        self.assertEqual(categoria.nombre, 'Postres')
        self.assertTrue(categoria.descripcion == '' or categoria.descripcion is None)


class ItemModelTest(TestCase):
    """Tests para el modelo Item"""
    
    def setUp(self):
        """Configuración inicial"""
        self.categoria = CategoriaItem.objects.create(
            nombre='Platos Principales',
            descripcion='Comidas principales'
        )
        self.item = Item.objects.create(
            nombre='Cazuela de Vacuno',
            descripcion='Cazuela tradicional chilena con carne de vacuno',
            categoria=self.categoria,
            precio=Decimal('8500'),
            disponible=True,
            tiempo_preparacion=30
        )
    
    def test_crear_item(self):
        """Test: Crear un item correctamente"""
        self.assertEqual(self.item.nombre, 'Cazuela de Vacuno')
        self.assertEqual(self.item.precio, Decimal('8500'))
        self.assertTrue(self.item.disponible)
        self.assertEqual(self.item.tiempo_preparacion, 30)
    
    def test_str_item(self):
        """Test: Representación en string del item"""
        # El __str__ del modelo incluye el precio
        self.assertIn('Cazuela de Vacuno', str(self.item))
    
    def test_relacion_categoria(self):
        """Test: Relación con categoría"""
        self.assertEqual(self.item.categoria, self.categoria)
        self.assertIn(self.item, self.categoria.items.all())
    
    def test_item_disponible_por_defecto(self):
        """Test: Item es disponible por defecto"""
        item = Item.objects.create(
            nombre='Pastel de Choclo',
            categoria=self.categoria,
            precio=Decimal('7500'),
            tiempo_preparacion=25
        )
        self.assertTrue(item.disponible)
    
    def test_precio_decimal(self):
        """Test: El precio es un valor Decimal"""
        self.assertIsInstance(self.item.precio, Decimal)
        self.assertGreater(self.item.precio, 0)
    
    def test_item_sin_categoria(self):
        """Test: Item puede existir sin categoría (null=True)"""
        item = Item.objects.create(
            nombre='Item Especial',
            descripcion='Sin categoría',
            precio=Decimal('10000'),
            tiempo_preparacion=20
        )
        self.assertIsNone(item.categoria)


# ============================================
# TESTS DE FORMULARIOS
# ============================================

class CategoriaItemFormTest(TestCase):
    """Tests para CategoriaItemForm"""
    
    def test_formulario_valido(self):
        """Test: Formulario con datos válidos"""
        form_data = {
            'nombre': 'Bebidas',
            'descripcion': 'Todo tipo de bebidas'
        }
        form = CategoriaItemForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_sin_nombre(self):
        """Test: Formulario sin nombre es inválido"""
        form_data = {'descripcion': 'Descripción sin nombre'}
        form = CategoriaItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
    
    def test_formulario_solo_nombre(self):
        """Test: Formulario solo con nombre es válido"""
        form_data = {'nombre': 'Sopas'}
        form = CategoriaItemForm(data=form_data)
        self.assertTrue(form.is_valid())


class ItemFormTest(TestCase):
    """Tests para ItemForm"""
    
    def setUp(self):
        """Configuración inicial"""
        self.categoria = CategoriaItem.objects.create(nombre='Carnes')
    
    def test_formulario_valido(self):
        """Test: Formulario con datos válidos"""
        form_data = {
            'nombre': 'Bife Chorizo',
            'descripcion': 'Bife de chorizo a la parrilla',
            'categoria': self.categoria.id,
            'precio': '15000',
            'disponible': True,
            'tiempo_preparacion': 20
        }
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_sin_precio(self):
        """Test: Formulario sin precio es inválido"""
        form_data = {
            'nombre': 'Item sin precio',
            'categoria': self.categoria.id,
            'tiempo_preparacion': 15
        }
        form = ItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)
    
    def test_formulario_precio_negativo(self):
        """Test: Precio negativo es inválido"""
        form_data = {
            'nombre': 'Item',
            'precio': '-1000',
            'tiempo_preparacion': 10
        }
        form = ItemForm(data=form_data)
        self.assertFalse(form.is_valid())


# ============================================
# TESTS DE VISTAS
# ============================================

class CocinaViewsTest(TestCase):
    """Tests para las vistas del módulo cocina"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.categoria = CategoriaItem.objects.create(
            nombre='Test Categoría',
            descripcion='Categoría de prueba'
        )
        self.item = Item.objects.create(
            nombre='Test Item',
            descripcion='Item de prueba',
            categoria=self.categoria,
            precio=Decimal('5000'),
            disponible=True,
            tiempo_preparacion=15
        )
    
    def test_cocina_index_view(self):
        """Test: Vista principal de cocina"""
        response = self.client.get(reverse('cocina:cocina_index'))
        self.assertEqual(response.status_code, 200)
    
    def test_listar_items_view(self):
        """Test: Vista de lista de items"""
        response = self.client.get(reverse('cocina:listar_items'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
    
    def test_detalle_item_view(self):
        """Test: Vista de detalle de item"""
        response = self.client.get(reverse('cocina:ver_item', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
        self.assertContains(response, '5000')
    
    def test_listar_categorias_view(self):
        """Test: Vista de lista de categorías"""
        response = self.client.get(reverse('cocina:listar_categorias'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Categoría')
    
    def test_crear_categoria_view_get(self):
        """Test: Vista de creación de categoría (GET)"""
        response = self.client.get(reverse('cocina:crear_categoria'))
        self.assertEqual(response.status_code, 200)
    
    def test_crear_item_view_get(self):
        """Test: Vista de creación de item (GET)"""
        response = self.client.get(reverse('cocina:crear_item'))
        self.assertEqual(response.status_code, 200)


# ============================================
# TESTS DE FILTROS
# ============================================

class FiltrosItemsTest(TestCase):
    """Tests para los filtros de items"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.categoria1 = CategoriaItem.objects.create(nombre='Entradas')
        self.categoria2 = CategoriaItem.objects.create(nombre='Postres')
        
        self.item_disponible = Item.objects.create(
            nombre='Item Disponible',
            categoria=self.categoria1,
            precio=Decimal('6000'),
            disponible=True,
            tiempo_preparacion=10
        )
        
        self.item_no_disponible = Item.objects.create(
            nombre='Item No Disponible',
            categoria=self.categoria2,
            precio=Decimal('7000'),
            disponible=False,
            tiempo_preparacion=15
        )
    
    def test_filtrar_por_disponibilidad(self):
        """Test: Filtrar items disponibles"""
        response = self.client.get(reverse('cocina:listar_items') + '?disponible=true')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Item Disponible')
    
    def test_filtrar_por_categoria(self):
        """Test: Filtrar items por categoría"""
        response = self.client.get(reverse('cocina:listar_items') + f'?categoria={self.categoria1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Item Disponible')


# ============================================
# TESTS DE INTEGRACIÓN
# ============================================

class IntegracionCocinaTest(TestCase):
    """Tests de integración para el módulo cocina"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
    
    def test_flujo_completo_creacion_item(self):
        """Test: Flujo completo de crear categoría e item"""
        # 1. Crear una categoría
        categoria = CategoriaItem.objects.create(
            nombre='Ensaladas',
            descripcion='Ensaladas frescas'
        )
        self.assertEqual(CategoriaItem.objects.count(), 1)
        
        # 2. Crear un item en esa categoría
        item = Item.objects.create(
            nombre='Ensalada César',
            descripcion='Ensalada clásica con pollo',
            categoria=categoria,
            precio=Decimal('6500'),
            disponible=True,
            tiempo_preparacion=10
        )
        
        # 3. Verificar relación
        self.assertEqual(item.categoria, categoria)
        self.assertEqual(categoria.items.count(), 1)
        
        # 4. Cambiar disponibilidad
        item.disponible = False
        item.save()
        self.assertFalse(item.disponible)
        
        # 5. Verificar que se puede recuperar
        item_db = Item.objects.get(nombre='Ensalada César')
        self.assertEqual(item_db.precio, Decimal('6500'))
        self.assertFalse(item_db.disponible)
