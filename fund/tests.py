import unittest
import json
import bcrypt

from my_settings            import WEDIZ_SECRET
from django.test     import TestCase, Client
from unittest.mock          import patch, MagicMock
from fund.views      import *
from fund.models     import FundProject, FundMainAgreement, Document, FundMainInformation, FundCategory, FundStory, StoryPhoto
from account.models  import User, ProfileInterest, UserGetInterest, Maker, SocialPlatform

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

class FundProjectTest (TestCase):

    def setUp(self):
        platform_dicts ={'wediz':1, 'kakao':2, 'google':3}

        for key, value in platform_dicts.items():
            SocialPlatform(
                id       = value,
                platform = key,
            ).save()

        user = User.objects.create(
            id               = 100,
            email            = 'b1234@na.com',
            user_name        = 'oiling',
            password         = decode_password,
            is_agree         = True,
            promotion        = False,
            is_maker         = False,
            company          = None,
            company_position = None,
            university       = None,
            major            = None,
            main_address     = None,
            sub_address      = None,
            introduction     = None,
            social           = SocialPlatform.objects.get(id=1),
            social_login_id  = '1234'
        )

        user_interest = ProfileInterest.objects.create(
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

        user_user_interest = UserGetInterest.objects.create(
            user             = user,
            profile_interest = user_interest
            )

        maker = Maker.objects.create(
            id               = 1,
            user             = user,
            name             = "나길동",
            kind             = "의류",
            phone_number     = "01077777777",
            is_agreed        = True
        )

        a =FundCategory.objects.create(
                id   = 1,
                name = "테크가전"
        )

        fmi = FundMainInformation.objects.create(
                id              = 1,
                title           = "xk",
                goal_money      = 1,
                category        = a,
                deadline        = "2000-01-01",
                is_adult_agreed = True,
                maker           = maker
        )

        document = Document.objects.create(
                id   = 2,
                name = "서류"
        )

        fma = FundMainAgreement.objects.create(
                id                    = 1,
                q1                    = 1,
                q2                    = 2,
                q3                    = "네 동의 합니다",
                q4                    = "동의하지 않아요~",
                is_commision_agreed   = True,
                is_futureopen_agreed  = False,
                document              = document,
                maker                 = maker
        )

        policy_document = PolicyDocument.objects.create(
                id = 5,
                name = "통신법"
        )

        fp = FundPolicy.objects.create(
                id                    = 1,
                q1                    = "yes",
                q2                    = 1,
                q3                    = "yes", 
                q4                    = "yes",
                is_auth_agreed        = True,
                is_commision          = True,
                is_opened             = True,
                document_id           = policy_document.id,
                maker                 = maker
        )

        fm = FundMaker.objects.create(
                id                    = 1,
                company_name          = "mycompany", 
                cs_email              = "hello@world.com", 
                cs_number             = "01000000000" , 
                ceo_name              = "지니", 
                ceo_email             = "genie@mail.com", 
                kakao_id              = "genie",
                kakao_link            = "kakao:genie.com",
                hompage               = "hp:myhome.com",
                sns1                  = "카카오", 
                sns2                  = "라인",
                sns3                  = "페북",
                maker                 = maker
        )
        fundstory = FundStory.objects.create(
                id            = 1,
                summary       = 'fs2',
                is_agreed     = True,
                context       = 'cpm',
                maker         = maker
        )

        storyphoto = StoryPhoto.objects.create(
                id         = fundstory.id,
                photo      = "awss3"
        )

        fundproject = FundProject.objects.create(
                id                         = 1,
                fund_main_agreement_id     = fmi.id,
                fund_main_information_id   = fma.id,
                fund_policies_id           = fp.id,
                fund_makers_id             = fm.id,
                maker_id                   = maker.id
        )

    def test_fundinfo_get(self):
        c = Client()
        
        test = {"email" : 'b1234@na.com', 'password' : password}
        response = c.post("/account/signin", json.dumps(test), content_type='applications/json')
        valid_token = response.json()["VALID_TOKEN"]
        
        response = c.get("/fund/maininfo",**{"HTTP_AUTHORIZATION": valid_token, "content_type":"applications/json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
                response.json(),
                {
                    'data': [
                        {
                        'id'             : 1,
                        'title'          : 'xk',
                        'goal_money'     : 1,
                        'main_image'     : None,
                        'category_id'    : 1,
                        'deadline'       : '2000-01-01',
                        'is_adult_agreed': True,
                        'maker_id'       : 1
                        }
                    ]
                })

    def test_fundmainagreement_get(self):
        c = Client()
        
        test = {"email" : 'b1234@na.com', 'password' : password}
        response = c.post("/account/signin", json.dumps(test), content_type='applications/json')
        
        valid_token = response.json()["VALID_TOKEN"]
        response = c.get('/fund/agreement',**{"HTTP_AUTHORIZATION": valid_token, "content_type":"applications/json"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
                response.json(),
                {
                    "data": [
                        {
                        'id': 1,
                        'q1': 1,
                        'q2': 2,
                        'q3': '네 동의 합니다',
                        'q4': '동의하지 않아요~',
                        'is_commision_agreed': True,
                        'is_futureopen_agreed': False,
                        'document_id': 2,
                        'maker_id': 1
                        }
                    ]
                })
    

    def test_fundpolicy_get(self):
        c = Client()
        
        test = {"email" : 'b1234@na.com', 'password' : password}
        response = c.post("/account/signin", json.dumps(test), content_type='applications/json')
        
        valid_token = response.json()["VALID_TOKEN"]
        response = c.get('/fund/policy',**{"HTTP_AUTHORIZATION": valid_token, "content_type":"applications/json"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
                response.json(),
                {
                    "data": [
                        {
                            "id": 1,
                            "q1": "yes",
                            "q2": 1,
                            "q3": "yes",
                            "q4": "yes",
                            "is_auth_agreed": True,
                            "is_commision": True,
                            "is_opened": True,
                            "document_id": 5,
                            "maker_id": 1
                        }
                    ]
                })
    def test_fundmaker_get(self):
        c = Client()
        
        test = {"email" : 'b1234@na.com', 'password' : password}
        response = c.post("/account/signin", json.dumps(test), content_type='applications/json')
        
        valid_token = response.json()["VALID_TOKEN"]
        response = c.get('/fund/makerinfo',**{"HTTP_AUTHORIZATION": valid_token, "content_type":"applications/json"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
                response.json(),
                {
                    "data": [
                        {
                            "id": 1,
                            "company_name": "mycompany",
                            "company_image": None,
                            "cs_email": "hello@world.com",
                            "cs_number": "01000000000",
                            "ceo_name": "지니",
                            "ceo_email": "genie@mail.com",
                            "kakao_id": "genie",
                            "kakao_link": "kakao:genie.com",
                            "hompage": "hp:myhome.com",
                            "sns1": "카카오",
                            "sns2": "라인",
                            "sns3": "페북",
                            "maker_id": 1
                        }
                    ]
                })

    def test_fundproject_get(self):
        c = Client()
        
        test = {"email" : 'b1234@na.com', 'password' : password}
        response = c.post("/account/signin", json.dumps(test), content_type='applications/json')
        
        valid_token = response.json()["VALID_TOKEN"]
        response = c.get('/fund/project',**{"HTTP_AUTHORIZATION": valid_token, "content_type":"applications/json"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
                response.json(),
                {
                    "data": [
                        {
                            "id": 1,
                            "fund_main_agreement_id": 1,
                            "fund_main_information_id": 1,
                            "fund_policies_id": 1,
                            "fund_makers_id": 1,
                            "maker_id": 1
                        }
                    ]
                })

    def tearDown(self):
        
        FundMainInformation.objects.all().delete()        
        FundCategory.objects.all().delete()
        FundMainAgreement.objects.all().delete()
        Document.objects.all().delete()
        User.objects.all().delete()
        Maker.objects.all().delete()
        ProfileInterest.objects.all().delete()
        UserGetInterest.objects.all().delete()
        PolicyDocument.objects.all().delete()
        FundPolicy.objects.all().delete()
        FundMaker.objects.all().delete()
        FundProject.objects.all().delete()
