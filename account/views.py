import jwt
import json
import bcrypt
import boto3
import requests

from my_settings               import WEDIZ_SECRET
from django.http               import JsonResponse
from django.views              import View
from django.core.validators    import validate_email
from django.core.exceptions    import ValidationError
from django.db                 import IntegrityError

from fund.models               import Maker
from .models                   import User, UserGetInterest, ProfileInterest, SocialPlatform, Maker
from my_settings               import WEDIZ_SECRET, aws_s3
from .utils                    import login_decorator

class SignupView(View):
	def post(self, request):
		user_data =json.loads(request.body)

		try:
			validate_email(user_data["email"])
			if User.objects.filter(email=user_data["email"]).exists():
				return JsonResponse({"MESSAGE" : "THIS_IS_EMAIL_ALREADY_EXIST"}, status=400)
			else:
				byted_password  = bytes(user_data["password"], encoding='utf-8')
				hashed_password = bcrypt.hashpw(byted_password, bcrypt.gensalt())
				decode_password = hashed_password.decode('utf-8')
				user = User.objects.create(
						email        = user_data["email"],
						user_name    = user_data["user_name"],
						password     = decode_password,
						is_agree     = user_data["is_agree"],
						promotion    = user_data["promotion"],
                        phone_number = user_data['phone_number'], 
						is_maker     = False
						)
				default_interest = ProfileInterest.objects.create(
					education_kids       = False,
					fashion_beauty_goods = False,
					home_design_item     = False,
					concert_culture      = False,
					sport_mobility       = False,
					publishing           = False,
					animal               = False,
					tech_home_appliance  = False
				)
				UserGetInterest.objects.create(user=user, profile_interest = default_interest)
				return JsonResponse({"MESSAGE" : "SIGNUP_SUCCESS"}, status=200)

		except ValidationError:
			return JsonResponse({"MESSAGE" : "NOT_EMAIL_FORM"}, status =400)
		except KeyError:
			return JsonResponse({"MESSAGE" : "INVALID_PUT"}, status=400)

class SigninView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            validate_email(data["email"])
            user_data      = User.objects.get(email=data["email"])
            user_password  = user_data.password.encode('utf-8')
            byted_password = data['password'].encode('utf-8')

            if bcrypt.checkpw(byted_password, user_password):
                payload = {
                        "user_id"       : user_data.id,
                        "user_is_maker" : user_data.is_maker,
                        "exp"           : WEDIZ_SECRET['exp_time'],
                        }
                jwt_encode = jwt.encode(payload, WEDIZ_SECRET['secret'], algorithm="HS256")
                token = jwt_encode.decode("utf-8") 
                return JsonResponse({"VALID_TOKEN" : token}, status=200)

            else:
                return JsonResponse({"MESSAGE" : "INVALID_PASSWORD"}, status=401)
        except User.DoesNotExist:
            return JsonResponse({"MESSAGE" : "INVALID_USER"}, status=401)
        except KeyError:
            return JsonResponse({"MESSAGE" : "INVALID_INPUT"}, status=400)

class KakaoSigninView(View):
    def post(self, request):
        kakao_token  = request.headers["Authorization"]
        if not kakao_token:
            return JsonResponse({"MESSAGE" : "INVALID_KAKAO_TOKEN"}, status=400)

        headers      = ({'Authorization' : f"Bearer {kakao_token}"})
        url          = "https://kapi.kakao.com/v1/user/me"
        response     = requests.post(url, headers=headers, timeout=2)
        user_data    = response.json()
        try:
            if User.objects.filter(social_login_id=user_data['id']).exists():
                user = User.objects.get(social_login_id=user_data['id'])
                payload = {
                    "user_id"       : user.id,
                    "kakao_id"      : user.social_login_id,
                    "user_is_maker" : user.is_maker,
                    "exp"           : WEDIZ_SECRET['exp_time']
                    }
                jwt_encode = jwt.encode(payload, WEDIZ_SECRET['secret'], algorithm="HS256")
                return JsonResponse({"VALID_TOKEN" : jwt_encode.decode('utf-8')} , status=200)
            else:
                signup_user = User.objects.create(
                    email     = user_data['kakao_account']['email'],
                    social    = SocialPlatform.objects.get(id=2).id,
                    social_login_id = user_data['id']
                    )
                payload = {
                    "user_id"       : signup_user.id,
                    "kakao_id"      : signup_user.social_login_id,
                    "user_is_maker" : signup_user.is_maker,
                    "exp"           : WEDIZ_SECRET['exp_time']
                    }
                jwt_encode = jwt.encode(payload, WEDIZ_SECRET['secret'], algorithm="HS256")
                return JsonResponse({"VALID_TOKEN" : jwt_encode.decode('utf-8')}, status=200)
        except ValueError:
            return JsonResponse({"MESSAGE" : "INVALID_EMAIL"}, status=401)

class ModifiedUserInfo(View):
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        login_user = request.user
        profile = UserGetInterest.objects.get(user = request.user)
        try:
            login_user.company                            = data['company']
            login_user.company_position                   = data['company_position']
            login_user.university                         = data['university']
            login_user.major                              = data['major']
            login_user.main_address                       = data['main_address']
            login_user.sub_address                        = data['sub_address']
            login_user.introduction                       = data['introduction']
            profile.profile_interest.education_kids       = data['education_kids']
            profile.profile_interest.fashion_beauty_goods = data['fashion_beauty_goods']
            profile.profile_interest.home_design_item      = data['home_design_item']
            profile.profile_interest.concert_culture       = data['concert_culture']
            profile.profile_interest.sport_mobility        = data['sport_mobility']
            profile.profile_interest.publishing            = data['publishing']
            profile.profile_interest.animal                = data['animal']
            profile.profile_interest.tech_home_appliance   = data['tech_home_appliance']
            login_user.save()
            profile.profile_interest.save()
            return JsonResponse({"MESSAGE" : "SUCCESS"}, status=200)   
        except KeyError:
            return JsonResponse({"MESSAGE" : "INVALID_INPUT"}, status=400)

    @login_decorator
    def get(self, request):
        profile = UserGetInterest.objects.get(user = request.user)
        try:
            user_profile = {            
                "company"              : profile.user.company,
                "company_position"     : profile.user.company_position,
                "university"           : profile.user.university,
                "major"                : profile.user.major,
                "main_address"         : profile.user.main_address,
                "sub_address"          : profile.user.sub_address,
                "introduction"         : profile.user.introduction,
                "profile_photo"        : profile.user.profile_photo,
                "education_kids"       : profile.profile_interest.education_kids,
                "fashion_beauty_goods" : profile.profile_interest.fashion_beauty_goods,
                "home_design_item"     : profile.profile_interest.home_design_item,
                "concert_culture"      : profile.profile_interest.concert_culture,
                "sport_mobility"       : profile.profile_interest.sport_mobility,
                "publishing"           : profile.profile_interest.publishing,
                "animal"               : profile.profile_interest.animal,
                "tech_home_appliance"  : profile.profile_interest.tech_home_appliance,
            }
            return JsonResponse({ "user_profile" : user_profile}, status=200)
        except KeyError:
            return JsonResponse({"MESSAGE" : "INVALID_INPUT"}, status=400)
        except ValueError:
            return JsonResponse({"MESSAGE" : "INVALID_VALUE"}, status=401)

class ModifiedUserPhoto(View):
    @login_decorator
    def post(self,request):
        if request.FILES['photo']:
            user = request.user
            extension = request.FILES['photo'].name.split('.')[-1]
            file_name = str(user.id)+"."+extension
            aws_s3.upload_fileobj(
                request.FILES['photo'],
                "wedizprofile", 
                file_name,
                ExtraArgs={
                    "ContentType" : request.FILES['photo'].content_type
                }
            )
            photo_url = "https://s3.ap-northeast-2.amazonaws.com/wedizprofile"+"-"+file_name
            user.profile_photo = photo_url
            user.save()

            return JsonResponse({"MESSAGE" : "SUCCESS", "photo_url" : photo_url}, status=200)
        else:
            return JsonResponse({"MESSAGE" : "FILES_NOT_FOUND"}, status=404)

class MakerCreate(View):
    @login_decorator
    def get(self, request):
        user = request.user
        data = [{
            "user_name" : user.user_name,
            "user_email" : user.email
        }]
        return JsonResponse({"data": data}, status=200)

    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        try:
            request.user.is_maker = True
            Maker.objects.create(
                user            = request.user,
                name            = data['name'],
                kind            = data['kind'],
                phone_number    = data['phone_number'],
                is_agreed       = data['is_agreed'],
            )
            return JsonResponse({"MESSAGE" : "SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"MESSAGE" : "INVALID_INPUT"}, status=400)
        except IntegrityError:
            return JsonResponse({"MESSAGE" : "USER_IS_ALREADY_MAKER( )"}, status=409)

class MakerInfoView(View):
    @login_decorator
    def get(self, request):
        user = request.user
        maker = Maker.objects.get(user = user)
        data = [{
            "name" : maker.name,
            "kind" : maker.kind,
            "phone_number" : maker.phone_number,
            "is_agreed" : maker.is_agreed,
            "user_name" : maker.user.user_name,
            "user_email" : maker.user.email
        }]
        return JsonResponse({"DATA": data}, status=200)
