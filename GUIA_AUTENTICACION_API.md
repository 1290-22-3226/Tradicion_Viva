# Autenticacion de TRADICION VIVA

La autenticacion se mantiene dentro de Django y usa `CuentaDevoto` como fuente unica de usuarios. No es necesario instalar el repositorio Node `auth-service` ni duplicar la base de datos.

## API JWT

Todos los endpoints usan JSON:

- `POST /api/auth/login/`: recibe `{ "email": "...", "password": "..." }`.
- `POST /api/auth/refresh/`: recibe `{ "refreshToken": "..." }` y rota el par de tokens.
- `GET /api/auth/me/`: requiere `Authorization: Bearer <accessToken>`.
- `POST /api/auth/logout/`: limpia cookies; el cliente movil debe descartar tambien sus tokens.

El access token dura 15 minutos y el refresh token 30 dias. Los tokens se firman con `JWT_SECRET_KEY`; si no se define, se usa `SECRET_KEY`.

## Sesion web

El login web conserva la sesion Django existente y ahora permite mantenerla durante 30 dias con la casilla correspondiente. Sin marcarla, la sesion termina al cerrar el navegador.
