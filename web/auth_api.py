import secrets
from datetime import timedelta

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from hermandades.models import CuentaDevoto


class AuthenticationError(Exception):
    pass


def _jwt_secret():
    return getattr(settings, "JWT_SECRET_KEY", "") or settings.SECRET_KEY


def _encode_token(account, token_type, lifetime):
    now = timezone.now()
    return jwt.encode(
        {
            "sub": str(account.pk),
            "type": token_type,
            "iat": now,
            "exp": now + lifetime,
            "jti": secrets.token_urlsafe(16),
        },
        _jwt_secret(),
        algorithm="HS256",
    )


def issue_tokens(account):
    return {
        "accessToken": _encode_token(account, "access", timedelta(minutes=15)),
        "refreshToken": _encode_token(account, "refresh", timedelta(days=30)),
    }


def _decode_token(token, expected_type):
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as exc:
        raise AuthenticationError("Token inválido o expirado.") from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise AuthenticationError("Tipo de token no válido.")
    account = CuentaDevoto.objects.filter(pk=payload["sub"], activa=True).first()
    if not account:
        raise AuthenticationError("Cuenta no encontrada o inactiva.")
    return account


def _json_body(request):
    try:
        import json

        return json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return None


def _account_data(account):
    registration = account.inscripciones.order_by("creado_en").first()
    return {
        "id": account.pk,
        "email": account.correo,
        "name": registration.nombre_completo if registration else account.correo,
    }


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    data = _json_body(request)
    email = str((data or {}).get("email", "")).strip().lower()
    password = str((data or {}).get("password", ""))
    account = CuentaDevoto.objects.filter(correo__iexact=email, activa=True).first()
    if not email or not password or not account or not account.check_password(password):
        return JsonResponse({"error": "Credenciales incorrectas."}, status=401)

    account.ultimo_acceso = timezone.now()
    account.save(update_fields=["ultimo_acceso"])
    return JsonResponse({"user": _account_data(account), "tokens": issue_tokens(account)})


@csrf_exempt
@require_http_methods(["POST"])
def api_refresh(request):
    data = _json_body(request) or {}
    token = data.get("refreshToken") or request.COOKIES.get("refresh_token")
    if not token:
        return JsonResponse({"error": "Falta el refresh token."}, status=401)
    try:
        account = _decode_token(token, "refresh")
    except AuthenticationError as exc:
        return JsonResponse({"error": str(exc)}, status=401)
    return JsonResponse({"user": _account_data(account), "tokens": issue_tokens(account)})


@require_GET
def api_me(request):
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return JsonResponse({"error": "Falta el token Bearer."}, status=401)
    try:
        account = _decode_token(token, "access")
    except AuthenticationError as exc:
        return JsonResponse({"error": str(exc)}, status=401)
    return JsonResponse({"user": _account_data(account)})


@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    response = JsonResponse({"message": "Sesión cerrada correctamente."})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


