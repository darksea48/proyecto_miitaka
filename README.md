# 🍽️ Mi ITAKA - Sistema de Gestión de Restaurante

Sistema completo de gestión para restaurantes desarrollado con Django y MySQL. Sistema modular que separa la gestión de comedor (mesas, reservas, clientes, pedidos) y cocina (menú, items, categorías) para mayor escalabilidad y mantenibilidad.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple)

## 📋 Descripción

Mi ITAKA es una aplicación web modular diseñada para facilitar la gestión integral de un restaurante. El sistema está dividido en módulos independientes que permiten controlar el flujo de operaciones desde la reserva de mesas hasta la gestión del menú y pedidos, proporcionando una interfaz intuitiva y eficiente para el personal del restaurante.

> **📝 Nota sobre Terminología:** Se decidió utilizar el término "**Item**" en lugar de "**Plato**" en todo el sistema para englobar no solo platos de comida, sino también bebestibles (bebidas, jugos, gaseosas), cocteles, mocktails y cualquier otro producto del menú. Esto hace el sistema más versátil y adaptable a las necesidades reales del restaurante.

### 🏗️ Arquitectura Modular

El proyecto está estructurado en dos aplicaciones principales:

- **Módulo Comedor**: Gestión de mesas, clientes, reservas y pedidos
- **Módulo Cocina**: Gestión de menú, items (platos, bebidas, cocteles, etc.) y categorías

Esta separación permite:
- Mayor mantenibilidad del código
- Escalabilidad independiente de módulos
- Separación clara de responsabilidades
- Facilidad para agregar nuevos módulos (ej: Caja, Inventario)

## ✨ Características Principales

### 📦 Módulo Comedor

#### 🪑 Gestión de Mesas
- Registro y administración de mesas
- Estados en tiempo real (Disponible, Ocupada, Reservada, Mantenimiento)
- Visualización por capacidad y ubicación
- Interfaz de tarjetas con código de colores por estado

#### 👥 Gestión de Clientes
- Registro de clientes con datos de contacto
- Historial de reservas y pedidos
- Campo de observaciones para alergias y preferencias
- Búsqueda y filtrado de clientes

#### 📅 Sistema de Reservas
- Creación y gestión de reservas
- Pre-selección automática de mesas/clientes desde vistas de detalle
- Campos deshabilitados para prevenir cambios accidentales
- Validaciones de negocio integradas:
  - Control de capacidad de mesa
  - Prevención de reservas en fechas pasadas
  - Mensajes de error específicos por campo
- Filtrado de mesas por capacidad
- Estados de reserva (Pendiente, Confirmada, En Curso, Completada, Cancelada)
- Seguimiento de fecha y hora

#### 🛒 Gestión de Pedidos
- Creación de pedidos por mesa
- Detalle de pedidos con múltiples items del menú
- Cálculo automático de subtotales y totales
- Estados de pedido (Pendiente, En Preparación, Listo, Servido, Pagado)
- Observaciones personalizadas por item

### 🍳 Módulo Cocina

#### 🍕 Gestión de Menú
- Administración de items del menú (platos, bebidas, cocteles, mocktails, etc.)
- Categorías de items personalizables
- Control de disponibilidad
- Gestión de precios y tiempos de preparación
- Vista de catálogo con cards visuales
- Filtros por categoría y disponibilidad

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.8** - Framework web principal
- **Python 3.13** - Lenguaje de programación
- **MySQL** - Base de datos relacional
- **MySQLclient** - Conector Python-MySQL

### Frontend
- **Bootstrap 5.3.3** - Framework CSS
- **Font Awesome 7.0.1** - Iconos
- **Bootstrap Icons 1.13.1** - Iconos adicionales
- **jQuery 3.7.1** - Manipulación DOM
- **SweetAlert2** - Alertas y confirmaciones elegantes

## 📦 Instalación

### Prerrequisitos
- Python 3.13 o superior
- MySQL Server 8.0 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tuusuario/proyecto_itaka.git
cd proyecto_itaka
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**

Crear una base de datos MySQL:
```sql
CREATE DATABASE itaka_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Editar `Proy_Itaka/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'itaka_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

5. **Ejecutar migraciones**
```bash
# Crear migraciones para ambos módulos
python manage.py makemigrations cocina
python manage.py makemigrations comedor
# Aplicar migraciones
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Recolectar archivos estáticos**
```bash
python manage.py collectstatic
```

8. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

9. **Acceder a la aplicación**
- Aplicación principal: http://localhost:8000/
- Módulo Comedor: http://localhost:8000/comedor/
- Módulo Cocina: http://localhost:8000/cocina/
- Panel de administración: http://localhost:8000/admin/

## 🗂️ Estructura del Proyecto

```
proyecto_itaka/
│
├── comedor/                    # Aplicación: Gestión de Comedor
│   ├── migrations/            # Migraciones de base de datos
│   ├── templates/             # Plantillas HTML del comedor
│   │   ├── index.html
│   │   ├── index_comedor.html
│   │   ├── list.html
│   │   ├── form_*.html
│   │   └── detail_*.html
│   ├── admin.py              # Admin: Mesas, Clientes, Reservas, Pedidos
│   ├── models.py             # Modelos: Mesa, Cliente, Reserva, Pedido
│   ├── views.py              # Vistas del módulo comedor
│   ├── urls.py               # URLs: /comedor/*
│   └── forms.py              # Formularios del comedor
│
├── cocina/                    # Aplicación: Gestión de Cocina
│   ├── migrations/            # Migraciones de base de datos
│   ├── templates/             # Plantillas HTML de cocina
│   │   └── cocina/
│   │       ├── index_cocina.html
│   │       ├── list_items.html
│   │       ├── form_item.html
│   │       ├── detail_item.html
│   │       ├── list_categorias.html
│   │       └── form_categoria.html
│   ├── admin.py              # Admin: Items, Categorías
│   ├── models.py             # Modelos: CategoriaItem, Item
│   ├── views.py              # Vistas del módulo cocina
│   ├── urls.py               # URLs: /cocina/*
│   └── forms.py              # Formularios de cocina
│
├── app_usuarios/              # Aplicación: Autenticación
│   ├── templates/             # Plantillas de login/registro
│   ├── views.py              # Vistas de autenticación
│   └── urls.py               # URLs de usuarios
│
├── Proy_Itaka/               # Configuración del proyecto
│   ├── settings.py           # Configuración general
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # Configuración WSGI
│
├── static/                   # Archivos estáticos
│   └── css/
│       └── styles.css        # Estilos personalizados
│
├── templates/                # Plantillas base
│   └── base.html            # Template base del proyecto
│
├── manage.py                # Script de gestión Django
├── requirements.txt         # Dependencias del proyecto
└── README.md               # Este archivo
```

## 📊 Modelos de Datos

### Módulo Comedor

#### Mesa
- Número de mesa (único)
- Capacidad (personas)
- Ubicación
- Estado (Disponible, Ocupada, Reservada, Mantenimiento)

#### Cliente
- Nombre completo
- Teléfono
- Email (opcional)
- Observaciones
- Fecha de registro

#### Reserva
- Cliente (FK)
- Mesa (FK)
- Fecha y hora de reserva
- Número de personas
- Estado
- Usuario que creó la reserva
- Observaciones

#### Pedido
- Mesa (FK, opcional)
- Cliente (FK, opcional)
- Estado
- Total
- Usuario que atendió
- Fecha y hora del pedido
- Observaciones

#### DetallePedido
- Pedido (FK)
- Item (FK → cocina.Item)
- Cantidad
- Precio unitario
- Subtotal
- Observaciones

### Módulo Cocina

#### CategoriaItem
- Nombre
- Descripción

#### Item
- Nombre
- Descripción
- Categoría (FK)
- Precio
- Disponible
- Tiempo de preparación

### Relaciones entre Módulos

- `DetallePedido.item` → `cocina.Item`: Los pedidos del comedor referencian items del módulo cocina
- Esta relación permite mantener los módulos separados pero funcionalmente conectados

## 🎨 Características de la Interfaz

- **Diseño Responsivo**: Adaptado a dispositivos móviles, tablets y desktop
- **Código de Colores**: Sistema visual intuitivo por estados
- **Cards Interactivas**: Efecto hover y zoom en elementos
- **Confirmaciones Elegantes**: SweetAlert2 para operaciones críticas
- **Navegación Intuitiva**: Menús organizados por secciones
- **Formularios Validados**: Validación cliente y servidor con mensajes específicos por campo
- **Filtros Dinámicos**: JavaScript para mejor UX
- **Pre-selección Inteligente**: Campos se pre-llenan y deshabilitan cuando corresponde

## 🔐 Panel de Administración

El sistema incluye un panel de administración completo con:
- Gestión de usuarios y permisos
- CRUD completo de todos los modelos
- Filtros y búsquedas avanzadas
- Acciones en lote
- Registro de actividad

## 🚀 Funcionalidades Destacadas

### Arquitectura Modular
- **Separación de Responsabilidades**: Cada módulo tiene su propio conjunto de modelos, vistas, URLs y templates
- **Escalabilidad**: Fácil agregar nuevos módulos (Caja, Inventario, Reportes)
- **Mantenibilidad**: Código organizado y fácil de mantener
- **Reutilización**: Los modelos pueden referenciarse entre módulos

### Funcionalidades Específicas del Sistema (v1.2)

#### 1. Gestión Automática del Ciclo de Vida de Mesas
**Flujo Completo:**
```
1. Mesa Disponible → Crear Reserva → Mesa Reservada
2. Mesa Reservada → Recepcionar Cliente → Mesa Ocupada + Reserva En Curso  
3. Mesa Ocupada → Crear/Editar Pedido → Gestión del pedido
4. Mesa Ocupada → Liberar Mesa → Mesa Disponible (si no hay más reservas)
```

**Implementación Inteligente:**
- El método `save()` del modelo `Reserva` actualiza automáticamente el estado de la mesa
- Valida si existen otras reservas activas antes de liberar
- Estados sincronizados entre Mesa ↔ Reserva

#### 2. Pre-selección Inteligente de Campos
Al navegar desde vistas de detalle, los campos se pre-cargan automáticamente:
- **Desde detalle de Mesa**: Campo mesa pre-seleccionado y deshabilitado en nueva reserva
- **Desde detalle de Cliente**: Campo cliente pre-seleccionado y deshabilitado en nueva reserva  
- **Desde detalle de Categoría**: Categoría pre-seleccionada al agregar nuevo item
- Campos `disabled` con `required=False` para evitar errores de validación

#### 3. Validaciones de Negocio Avanzadas
Implementadas con mensajes específicos por campo:
- **Capacidad de Mesa**: No se puede reservar más personas de las que caben
- **Fecha Válida**: No se permiten reservas en fechas pasadas
- **Estado de Mesa**: Validación de disponibilidad antes de reservar
- **Reserva Activa**: Búsqueda de reserva en curso antes de crear pedido
- Errores mostrados con `add_error()` en el campo correcto

#### 4. Búsqueda y Vinculación Automática de Reservas
Las vistas buscan inteligentemente reservas asociadas:
```python
# Recepcionar Mesa: busca reserva confirmada
reserva = Reserva.objects.filter(
    mesa=mesa, 
    estado__in=['pendiente', 'confirmada']
).first()

# Crear Pedido: busca reserva en curso  
reserva = Reserva.objects.filter(
    mesa=mesa,
    estado='en_curso'
).first()

# Detalle Mesa: muestra reserva actual
reserva_activa = Reserva.objects.filter(
    mesa=mesa,
    estado__in=['pendiente', 'confirmada', 'en_curso']
).first()
```

#### 5. Edición Inteligente de Pedidos (Sin Duplicados)
```python
# Buscar pedido existente
pedido_existente = Pedido.objects.filter(
    mesa=mesa,
    estado__in=['pendiente', 'en_preparacion', 'listo', 'servido']
).first()

if pedido_existente:
    # Editar pedido existente
    form = PedidoForm(instance=pedido_existente)
    messages.info(request, f'Editando pedido #{pedido_existente.id}')
else:
    # Crear nuevo pedido
    form = PedidoForm(initial={'mesa': mesa})
```

**Beneficios:**
- Previene pedidos duplicados por mesa
- UI dinámica: botones "Crear" vs "Editar"
- Experiencia de usuario mejorada

#### 6. Funcionalidades Generales
1. **Pre-selección de Campos**: Navegación contextual con campos automáticos
2. **Filtrado Inteligente**: Mesas por capacidad, items por categoría
3. **Cálculo Automático**: Totales de pedidos calculados en tiempo real
4. **Estados en Tiempo Real**: Sistema de badges con colores
5. **Historial Completo**: Tracking de fechas de creación y actualización
6. **Gestión Independiente**: Módulos cocina y comedor funcionan de forma autónoma pero integrada

## 🔮 Próximas Funcionalidades

El proyecto está en desarrollo activo y próximamente se agregarán los siguientes módulos en futuras versiones:

### 🍳 Módulo de Cocina - Operaciones en Tiempo Real (Versión 2.0)
El módulo de cocina actual gestiona el menú. En próximas versiones se agregará:
- Vista de pedidos en tiempo real para cocina
- Sistema de tickets de cocina
- Control de tiempos de preparación
- Notificaciones cuando los items están listos
- Dashboard de producción
- Estado de pedidos por estación de cocina

### 📦 Módulo de Bodega/Inventario de Cocina (Versión 2.0)
Sistema completo de gestión de inventario:
- Control de stock de ingredientes y materias primas
- Alertas de stock mínimo y crítico
- Gestión de proveedores y contactos
- Registro de compras y entradas
- Control de mermas y pérdidas
- Seguimiento de fechas de vencimiento
- Integración con recetas (consumo automático por item)
- Reportes de rotación de inventario
- Gestión de bodegas múltiples

### 💰 Módulo de Caja (Versión 2.5)
Sistema completo de gestión financiera:
- Gestión de pagos (efectivo, tarjeta, transferencia)
- Facturación electrónica
- Control de caja (apertura/cierre diario)
- Reportes de ventas diarias, semanales y mensuales
- Historial completo de transacciones
- Generación de boletas y facturas electrónicas
- Dashboard financiero con gráficos
- Control de propinas
- Arqueo de caja
- Integración con sistemas de pago (POS, QR)

### 📊 Módulo de Reportes y Análisis (Versión 3.0)
Business Intelligence para la gestión:
- Reportes de ventas por período (día/semana/mes/año)
- Estadísticas de items más vendidos
- Análisis de ocupación de mesas y rotación
- Reportes de desempeño del personal
- Análisis de rentabilidad por item
- Predicción de demanda
- Gráficos interactivos con Chart.js
- Exportación a PDF y Excel
- Dashboard ejecutivo

### 🎯 Mejoras Adicionales en Desarrollo
- **Sistema de Reservas Online**: Portal web para clientes
- **App Móvil**: Para meseros y gestión en tiempo real
- **Sistema de Fidelización**: Puntos y descuentos para clientes frecuentes
- **Integración con Delivery**: Uber Eats, Rappi, etc.
- **Sistema de Feedback**: Encuestas de satisfacción
- **Panel de Comandas Digital**: Tablets para meseros
- **Sistema de Cola de Espera**: Gestión de lista de espera
- **Notificaciones Push**: Alertas en tiempo real

### ✨ Funcionalidades Destacadas (Nuevas - v1.2)

#### Gestión Inteligente de Estado de Mesas
El sistema ahora maneja automáticamente el ciclo de vida de las mesas:
- **Reserva creada/confirmada** → Mesa pasa a estado "Reservada"
- **Cliente recepcionado** → Mesa pasa a "Ocupada" y reserva a "En Curso"
- **Reserva cancelada/terminada** → Mesa vuelve a "Disponible" (si no hay otras reservas)
- Validación automática: verifica otras reservas activas antes de liberar

```python
# Implementación en modelo Reserva
def save(self, *args, **kwargs):
    if self.estado in ['pendiente', 'confirmada']:
        self.mesa.estado = 'reservada'
        self.mesa.save()
    elif self.estado in ['cancelada', 'terminada']:
        if not hay_otras_reservas_activas:
            self.mesa.estado = 'disponible'
            self.mesa.save()
```

#### Búsqueda Automática de Reservas Activas
Las vistas ahora buscan inteligentemente la reserva asociada a cada mesa:
- `recepcionar_mesa()`: Encuentra reserva confirmada para cambiar estados
- `crear_pedido_mesa()`: Busca reserva en curso para obtener datos del cliente
- `MesaDetailView`: Muestra información completa de la reserva actual

#### Edición Inteligente de Pedidos
El sistema previene duplicados y facilita la gestión:
- Detecta si ya existe un pedido activo para la mesa
- Si existe: carga el formulario con datos para edición
- Si no existe: crea un nuevo pedido
- Botones dinámicos en UI: "Crear Pedido" vs "Editar Pedido"
- Mensaje informativo: "Editando pedido existente #123"

### 🤔 Funcionalidades en Evaluación (Posible Versión 3.5)
Características que podrían incorporarse según necesidades del negocio:
- **Módulo de Personal y Turnos**: 
  - Control de turnos y horarios
  - Registro de asistencia
  - Gestión de roles y permisos avanzados
  - Seguimiento de comisiones y propinas
  - Evaluación de desempeño
  - Planificación de turnos
- **Sistema de Mesas 3D**: Visualización interactiva del restaurante
- **Integración con Contabilidad**: Sincronización con sistemas contables
- **Multi-sucursal**: Gestión de múltiples locales desde un solo sistema


## 📝 Configuración Adicional

### Zona Horaria
El proyecto está configurado para `America/Santiago` (Chile). Para cambiar:
```python
# settings.py
TIME_ZONE = 'tu_zona_horaria'
```

### Idioma
Configurado en español de Chile. Para cambiar:
```python
# settings.py
LANGUAGE_CODE = 'es-cl'
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.

## 👨‍💻 Autor

**Douglas Suárez Zamorano**

## 🙏 Agradecimientos

- Bootcamp Full Stack Python/Django por la formación
- Cynthia Castillo/Ricardo Vega, mis profesores, por la formación
- Valeria Jara Bugueño, mi esposa, por el apoyo y la contención
- Cristian Astudillo/Gerard Bourguett, mis amigos, similar motivo del anterior
- Comunidad Django por la documentación
- Bootstrap por el framework CSS

## 📧 Contacto

Para preguntas o sugerencias, puedes contactar al desarrollador.

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub
