# TRADICIÓN VIVA – Cambios de identidad visual y administradores por organización

## 1. Identidad visual tomada del logotipo

La interfaz general ahora utiliza una paleta basada en el logotipo de TRADICIÓN VIVA:

- Morado principal: `#743A8B`
- Morado profundo: `#42194E`
- Lila: `#B88AC5`
- Crema: `#ECD5AE`
- Arena/dorado suave: `#CB9C64`

El encabezado general muestra el logotipo junto al texto **TRADICIÓN VIVA**. También se agregó el logotipo como favicon.

Las páginas propias de cada hermandad o cofradía siguen respetando sus colores institucionales configurados en Django (`color_primario` y `color_acento`).

## 2. Panel del devoto con color de cada organización

En **Mi cuenta**, cada inscripción usa automáticamente:

- `hermandad.color_primario`
- `hermandad.color_acento`
- `hermandad.logo`

Por lo tanto, si un devoto está inscrito en varias organizaciones, cada recuadro se verá con la identidad visual de la organización correspondiente y mostrará su logo junto al nombre.

## 3. Administradores limitados a una hermandad o cofradía

Se agregó el modelo `AdministradorOrganizacion`.

Cada usuario administrativo normal puede quedar asignado a **una sola hermandad o cofradía**. Una organización puede tener varios administradores si se necesita.

Un administrador asignado solamente puede consultar o modificar datos de su propia organización en:

- Hermandad/Cofradía
- Turnos del recorrido
- Agenda
- Devotos
- Imágenes
- Videos
- Marchas / repertorio
- Comunicados
- Historial de envíos

Además, el editor personalizado de turnos valida la asignación, por lo que no basta con escribir manualmente la URL de otra organización.

Las cuentas globales de devotos (`CuentaDevoto`) quedan reservadas al superusuario porque un mismo correo puede estar relacionado con más de una organización.

### Importante sobre el superusuario

El **superusuario conserva acceso total a todas las organizaciones**. Esto es intencional.

Para comprobar la restricción, no debes probar con la cuenta `admin` si esa cuenta es superusuario. Debes crear un usuario administrativo normal y asignarlo a una organización.

## 4. Pasos obligatorios después de reemplazar el proyecto

Desde la carpeta que contiene `manage.py`:

```powershell
python manage.py migrate
```

Luego inicia el proyecto normalmente:

```powershell
python manage.py runserver
```

En producción también ejecuta, si corresponde:

```powershell
python manage.py collectstatic --noinput
```

## 5. Cómo crear un administrador de una organización

1. Entra a `/admin/` con el **superusuario**.
2. Ve a **Usuarios** y crea el usuario que utilizará el administrador. Déjalo activo y **no lo conviertas en superusuario**.
3. Ve a **Asignaciones de administradores** dentro de la aplicación de hermandades.
4. Crea una asignación seleccionando:
   - Usuario administrativo.
   - Hermandad o cofradía.
   - Activo = Sí.
5. Al guardar la asignación, el sistema marca automáticamente ese usuario como `is_staff=True`.
6. Cierra la sesión del superusuario.
7. Ingresa desde **Iniciar sesión → Administrativo** con el nuevo usuario.

Ese usuario verá únicamente la organización que tenga asignada y sus registros asociados.

## 6. Archivos principales modificados

- `web/templates/web/base.html`
- `web/templates/web/home.html`
- `web/templates/web/iniciar_sesion.html`
- `web/templates/web/devoto_login.html`
- `web/templates/web/administrativo_login.html`
- `web/templates/web/devoto_password_reset.html`
- `web/templates/web/devoto_password_reset_confirm.html`
- `web/templates/web/devoto_panel.html`
- `web/static/web/img/tradicion_viva_logo.png`
- `hermandades/models.py`
- `hermandades/admin.py`
- `hermandades/migrations/0014_administradororganizacion.py`
- `web/views.py`
- `web/tests.py`

## 7. Validación realizada

Se verificó la sintaxis de todos los archivos Python del proyecto con `py_compile` y la estructura básica de los bloques de las plantillas modificadas.

En este entorno no fue posible ejecutar `python manage.py check` porque Django no está instalado globalmente aquí; en tu computadora, con el entorno del proyecto activado y `requirements.txt` instalado, debes ejecutar `python manage.py migrate` y luego iniciar el servidor.
