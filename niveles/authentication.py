import firebase_admin
from firebase_admin import auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class FirebasePrincipal:
    is_authenticated = True
    is_anonymous = False

    def __init__(self, uid):
        self.uid = uid


class FirebaseAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return "Bearer"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Usa Authorization: Bearer <token>.")

        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()

        try:
            decoded = auth.verify_id_token(parts[1])
        except (auth.InvalidIdTokenError, ValueError) as error:
            raise AuthenticationFailed("Token de Firebase inválido o vencido.") from error

        uid = decoded.get("uid")
        if not isinstance(uid, str) or not uid:
            raise AuthenticationFailed("El token de Firebase no contiene un UID válido.")

        return FirebasePrincipal(uid), decoded
