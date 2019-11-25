import jwt
import json
import bcrypt
from django.http    import JsonResponse,HttpResponse
from account.models import User, Maker
from fund.models    import FundProject, FundMainAgreement, FundMainInformation, FundPolicy, FundMaker
from my_settings    import WEDIZ_SECRET

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs): 
   
        if "Authorization" not in request.headers: 
            return JsonResponse({"ERROR_CODE":"INVALID_LOGIN"}, status=401)
        
        encode_token = request.headers["Authorization"] 
        
        try:
            data = jwt.decode(encode_token, WEDIZ_SECRET['secret'], algorithm='HS256') 
            user = User.objects.select_related('users').get(id = data["user_id"])
            request.user = user
             
            if user.users.is_agreed == False:
                return JsonResponse({"ERROR_CODE":"INVALID_MAKER"}, status = 403)

        except jwt.DecodeError: 
            return JsonResponse({"ERROR_CODE" : "INVALID_TOKEN"}, status = 401) 
        
        except User.DoesNotExist:
            return JsonResponse({"ERROR_CODE" : "UNKNOWN_USER"}, status = 401)
        
        return func(self, request, *args, **kwargs) 
    
    return wrapper
