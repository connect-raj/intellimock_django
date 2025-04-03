import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class JWTCookieAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: self.get_authenticated_user(request))
        return self.get_response(request)

    def get_authenticated_user(self, request):
        jwt_token = request.COOKIES.get('jwt_token')

        if not jwt_token:
            return AnonymousUser()

        try:
            # Decode JWT token
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if not user_id:
                return AnonymousUser()

            # Fetch user from the database
            user = User.objects.filter(id=user_id).first()
            return user if user else AnonymousUser()

        except jwt.ExpiredSignatureError:
            print("JWT Token expired")
        except jwt.DecodeError:
            print("Error decoding JWT Token")
        except Exception as e:
            print(f"Authentication error: {str(e)}")

        return AnonymousUser()
