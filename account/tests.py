import json
import boto3
import bcrypt
import jwt

from PIL                    import Image
from django.test            import TestCase, Client
from unittest.mock          import patch, MagicMock
from io                     import BytesIO
from django.core.files.base import ContentFile

from account.models         import User, ProfileInterest, UserGetInterest, SocialPlatform, Maker
from my_settings            import WEDIZ_SECRET

def create_image(storage, filename, size=(30,30), image_mode = 'RGB', image_format='PNG'):
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    if not storage:
        return data
    image_file = ContentFile(data.read())
    return storage.save(filename, image_file)

password = '1234'
byted_password  = bytes(password, encoding='utf-8')
hashed_password = bcrypt.hashpw(byted_password, bcrypt.gensalt())
decode_password = hashed_password.decode('utf-8')

class UserTest(TestCase):
    maxDiff = None

    def setUp(self):
        cl = Client()

        platform_dicts ={'wediz':1, 'kakao':2, 'google':3}

        for key, value in platform_dicts.items():
            SocialPlatform(
                id       = value,
                platform = key,
            ).save()

        test = User.objects.create(
            id        = 100,
            email     = 'b1234@na.com',
            user_name = 'oiling',
            password  = decode_password,
            is_agree  = True,
            promotion = False,
            is_maker  = False,
            company   = None,
            company_position = None,
            university = None,
            major  = None,
            main_address = None,
            sub_address = None,
            introduction = None,
            social       = SocialPlatform.objects.get(id=1),
            social_login_id = '1234'
        )

        maker = Maker.objects.create(
            id           = 1,
            user         = test,
            name         = "나길동",
            kind         = "의류",
            phone_number = "10202030",
            is_agreed    = True
        )

        test_interest = ProfileInterest.objects.create(
            id                   = 100,
            education_kids       = False,
            fashion_beauty_goods = False,
            home_design_item     = False,
            concert_culture      = False,
            sport_mobility       = False,
            publishing           = False,
            animal               = False,
            tech_home_appliance  = False
            )
        test_user_interest = UserGetInterest.objects.create(
            user             = test,
            profile_interest = test_interest
            )

    def test_user_signin(self):
        cl = Client()

        test        = {"email":'b1234@na.com', 'password' : password}
        response    = cl.post("/account/signin", json.dumps(test), content_type="application/json")
        valid_token = response.json()['VALID_TOKEN']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"VALID_TOKEN" : valid_token})

    def test_user_invalid_user_signin(self):
        cl = Client()

        test        = {"email":'b1231234@na.com', 'password' : '123password'}
        response    = cl.post("/account/signin", json.dumps(test), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_user_invalid_password_signin(self):
        cl = Client()

        test        = {"email":'b1234@na.com', 'password' : '123password'}
        response    = cl.post("/account/signin", json.dumps(test), content_type="application/json")
        self.assertEqual(response.status_code, 401)



    @patch('account.views.requests')
    def test_kakao_signin(self, mocked_requests):
        cl = Client()
        mock_value_dict = {"id" : "1234", "kakao_account" : { "email" : "b1234@na.com"}}

        class MockedResponse:
            def json(self):
                return mock_value_dict

        mocked_requests.post = MagicMock(return_value = MockedResponse())
        test = {
            "social_login_id" : "1234",
            "email" : "b1234@na.com",
            "password" : password
        }
        response = cl.post('/account/kakaosignin', json.dumps(test),**{"HTTP_AUTHORIZATION":"1234","content_type":"application/json"})
        valid_token = response.json()["VALID_TOKEN"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"VALID_TOKEN" : valid_token})

    def test_post_modifieduserinfo(self):
        cl = Client()

        test = {"email" : 'b1234@na.com', 'password' : password}
        response = cl.post("/account/signin", json.dumps(test), content_type='applications/json')
        valid_token = response.json()["VALID_TOKEN"]
        test = {
            'company': 'aa',
            'company_position' : 'decode_password',
            'university':'coll ',
            'major' : 'computer',
            'main_address' : 'seoul',
            'sub_address': 'we work',
            'introduction' : 'hi everyone',
            'education_kids' : True,
            'fashion_beauty_goods': True,
            'home_design_item': False,
            'concert_culture': False,
            'sport_mobility': False,
            'publishing':False ,
            'animal': False,
            'tech_home_appliance': False
        }

        response = cl.post("/account/modifyprofile", json.dumps(test),**{"HTTP_AUTHORIZATION": valid_token, "content_type":"applications/json"})
        self.assertEqual(response.status_code, 200)

    def test_get_userinfo(self):
        cl = Client()

        test = {"email" : 'b1234@na.com', "password" : password}
        response = cl.post("/account/signin", json.dumps(test), content_type='applications/json')
        valid_token = response.json()["VALID_TOKEN"]
        response = cl.get("/account/modifyprofile", **{"HTTP_AUTHORIZATION" : valid_token})
        self.assertEqual(response.status_code, 200)

    @patch("account.views.ModifiedUserPhoto.aws_s3")
    def test_modifieduserphoto(self, mocked_boto3):
        cl = Client()

        test = {"email" : "b1234@na.com", "password" : password}
        response = cl.post("/account/signin", json.dumps(test), content_type = "application/json")
        valid_token = response.json()["VALID_TOKEN"]
        profile_photo = create_image(None, "profile.png")
        form_data = { "photo" : profile_photo } 
        response = cl.post("/account/modifyprofilephoto", form_data, **{"HTTP_AUTHORIZATION" : valid_token})

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "https://s3.ap-northeast-2.amazonaws.com/wedizprofile",
            response.json()['photo_url']
        )

    def test_post_makercreate(self):
        cl = Client()

        test = {
            "email" : 'c1234@na.com',
            "password" : password,
            "user_name" : "user_name",
            "password" : password,
            "is_agree" :  True,
            "promotion" : True,
            "is_maker" : False
        }
        response = cl.post("/account/signup", json.dumps(test), content_type='applications/json')
        self.assertEqual(response.status_code, 200)
        test = {"email" : 'c1234@na.com', "password" : password}
        response = cl.post("/account/signin", json.dumps(test), content_type='applications/json')
        valid_token = response.json()["VALID_TOKEN"]
        test = {
            "name"         : "안녕",
            "kind"         : "com",
            "phone_number" : "011123445",
            "is_agreed"    : True
        }
        response = cl.post("/account/maker", json.dumps(test), **{"HTTP_AUTHORIZATION" : valid_token, "content_type" : "application/json"})
        self.assertEqual(response.status_code, 200)

    def test_get_makercreate(self):
        cl = Client()

        test = {"email" : 'b1234@na.com', "password" : password}
        response = cl.post("/account/signin", json.dumps(test), content_type='applications/json')
        valid_token = response.json()["VALID_TOKEN"]
        response = cl.get("/account/maker", **{"HTTP_AUTHORIZATION" : valid_token})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        UserGetInterest.objects.all().delete()
        User.objects.all().delete()
        ProfileInterest.objects.all().delete()
        Maker.objects.all().delete()
