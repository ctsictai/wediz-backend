import jwt
import json
import bcrypt
from django.http    import JsonResponse,HttpResponse
from account.models import User
from my_settings  import WEDIZ_SECRET

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs): 
   
        if "Authorization" not in request.headers: 
            return JsonResponse({"ERROR_CODE":"INVALID_LOGIN"}, status=401)
        
        encode_token = request.headers["Authorization"] 
        
        try:
            data = jwt.decode(encode_token, WEDIZ_SECRET['secret'], algorithm='HS256') 
            user = User.objects.get(id = data["user_id"])
            request.user = user 
        
        except jwt.DecodeError: 
            return JsonResponse({"ERROR_CODE" : "INVALID_TOKEN"}, status = 401) 
        
        except User.DoesNotExist:
            return JsonResponse({"ERROR_CODE" : "UNKNOWN_USER"}, status = 401) 
        
        return func(self, request, *args, **kwargs) 
    
    return wrapper
