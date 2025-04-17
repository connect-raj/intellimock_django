from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import jwt
from main.settings import SECRET_KEY

JWT_SECRET = SECRET_KEY  # Change this in production
JWT_ALGORITHM = 'HS256'

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')
        if not token:
            return JsonResponse({'error': 'No token provided'}, status=401)
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = payload['user_id']
            return view_func(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
    
    return wrapper 