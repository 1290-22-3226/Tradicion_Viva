# PostgreSQL y pgAdmin

TRADICIÓN VIVA puede seguir usando SQLite en desarrollo. Cuando `.env` tenga `PGDATABASE` o `DATABASE_URL`, Django utilizará PostgreSQL automáticamente.

## 1. Crear la base en PostgreSQL

En pgAdmin crea primero un usuario de aplicación que no sea superusuario y después una base de datos propiedad de ese usuario.

Valores sugeridos:

```text
Base de datos: tradicion_viva
Usuario: tradicion_viva_app
Host: 127.0.0.1
Puerto: 5432
```

Usa una contraseña larga y guárdala únicamente en `.env` o en el gestor de secretos del servidor.

## 2. Configurar Django

Copia `.env.example` como `.env` y completa:

```env
DEBUG=False
PGDATABASE=tradicion_viva
PGUSER=tradicion_viva_app
PGPASSWORD=tu-clave
PGHOST=127.0.0.1
PGPORT=5432
PGSSLMODE=prefer
DATABASE_SSL_REQUIRE=False
```

En producción administrada usa `PGSSLMODE=require` o `DATABASE_URL` con TLS. No subas `.env` al repositorio.

## 3. Crear las tablas

Desde la carpeta del proyecto ejecuta:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py check --deploy
```

Las migraciones crean las tablas compartidas. Los registros de cada organización se delimitan mediante su relación `hermandad_id`; el administrador de una organización solo debe ver los registros asignados a ella.

La migración `hermandades.0017_rls_organizacion` activa Row-Level Security en `Devoto`, `EventoAgenda`, `TurnoRecorrido`, `Comunicado` y `EnvioComunicado`. Django establece el contexto de la organización en cada petición. `CuentaDevoto` queda fuera porque una misma cuenta puede estar vinculada a varias organizaciones; el acceso del devoto se limita mediante su cuenta y sesión.

La información institucional, imágenes y vídeos públicos no tiene RLS porque debe poder consultarse sin iniciar sesión. Aun así, las operaciones administrativas sobre esos contenidos continúan filtradas por organización desde Django.

## 4. Migrar los datos actuales desde SQLite

Haz una copia del archivo `db.sqlite3` antes de empezar. Con SQLite activo exporta los datos:

```powershell
.\.venv\Scripts\python.exe manage.py dumpdata --natural-foreign --natural-primary --exclude auth.permission --exclude contenttypes --indent 2 > respaldo.json
```

Configura PostgreSQL en `.env`, ejecuta `migrate` y carga el respaldo:

```powershell
.\.venv\Scripts\python.exe manage.py loaddata respaldo.json
```

Revisa especialmente usuarios administrativos, archivos multimedia y registros de comunicaciones antes de eliminar SQLite.

## Verificar RLS desde pgAdmin

En la Query Tool de `tradicion_viva` puedes confirmar que las tablas privadas están protegidas:

```sql
SELECT relname, relrowsecurity, relforcerowsecurity
FROM pg_class
WHERE relname IN (
	'hermandades_devoto',
	'hermandades_eventoagenda',
	'hermandades_turnorecorrido',
	'hermandades_comunicado',
	'hermandades_enviocomunicado'
)
ORDER BY relname;
```

Las dos columnas deben aparecer como `true`. No desactives RLS manualmente desde pgAdmin; cualquier cambio debe quedar en una migración revisable.

## Delimitación de seguridad

Esta primera etapa prepara PostgreSQL y conserva una única estructura de tablas. No crea una base por organización todavía. El siguiente refuerzo será añadir pruebas de aislamiento y Row-Level Security de PostgreSQL, después de verificar que todas las consultas administrativas llevan el filtro de `hermandad_id` correcto.