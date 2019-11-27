import json
import jwt
import bcrypt
import datetime
import boto3

from django.views      import View
from django.http       import JsonResponse, HttpResponse
from django.db         import transaction

from my_settings       import WEDIZ_SECRET, aws_s3
from account.models    import Maker

from .models           import FundProject, FundMainAgreement, Document, FundCategory, FundMainInformation, PolicyDocument, FundPolicy, FundMaker, FundReward, StoryPhoto, FundStory
from .utils            import login_decorator

class FundDetailView(View):

    def get(self, request, fund_id):
        detail = FundProject.objects.prefetch_related('fundrewards','fund_main_information', 'fund_story').get(id = fund_id)

        result = {
            "reward": list(detail.fundrewards.values()),
            "fundstory_id" : detail.fund_story.id,
            "fundstory_context" :  detail.fund_story.context,
            "fundstory_summary" : detail.fund_story.summary,
            "fundstory_images": list(detail.fund_story.storyphotos.values()),
            "title": detail.fund_main_information.title,
            "targetGoad":detail.fund_main_information.goal_money,
            "mainImage":detail.fund_main_information.main_image,
            "category":detail.fund_main_information.category.name,
            "endDate":detail.fund_main_information.deadline,
        }
        return JsonResponse({"data" : result}, status = 200)

class MainInformation(View):
    @login_decorator
    def get(self, request):
        return JsonResponse({"data":list(FundMainInformation.objects.values())}, status = 200)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user = request.user
        data = json.loads(request.body)
        category_info = FundCategory.objects.get(id=data["category"])
        maininfo = FundMainInformation.objects.get(maker =user.users)

        try : 
            maininfo.title           = data["title"]
            maininfo.goal_money      = data["goal_money"]
            maininfo.category        = category_info
            maininfo.deadline        = data["deadline"]
            maininfo.is_adult_agreed = data["is_adult_agreed"]
            maininfo.maker           = user.users
            maininfo.save()
            return JsonResponse({"message":"SUCCESS"}, status = 200)

        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)

        except ValueError:
            return JsonResponse({"message":"ValueError"}, status = 401)


class MainAgreement(View):
    @login_decorator
    def get(self, request):
        return JsonResponse({"data":list(FundMainAgreement.objects.values())}, status = 200)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user = request.user
        data = json.loads(request.body)
        mainagreement = FundMainAgreement.objects.get(maker =user.users.id)

        try :      
            mainagreement.q1                    = data["q1"]
            mainagreement.q2                    = data["q2"]
            mainagreement.q3                    = data["q3"]
            mainagreement.q4                    = data["q4"]
            mainagreement.is_commision_agreed   = data["is_commision_agreed"]
            mainagreement.is_futureopen_agreed  = data["is_futureopen_agreed"]
            mainagreement.document_id           = data["document_id"]
            mainagreement.maker                 = user.users    
            mainagreement.save()

            return JsonResponse({"message":"SUCCESS"}, status = 200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)
        except ValueError:
            return JsonResponse({"message":"ValueError"}, status = 401)


class FundPolicyView(View):
    @login_decorator
    def get(self, request):
        return JsonResponse({"data":list(FundPolicy.objects.values())}, status = 200)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user = request.user
        data = json.loads(request.body)
        document_object = PolicyDocument.objects.get(id = data['document_id'])
        policy = FundPolicy.objects.get(maker =user.users.id)

        try:
            policy.q1                  = data['q1']
            policy.q2                  = data['q2']
            policy.q3                  = data['q3']
            policy.q4                  = data['q4']
            policy.is_auth_agreed      = data['is_auth_agreed']
            policy.is_commision        = data['is_commision']
            policy.is_opened           = data['is_opened']
            policy.document            = document_object
            policy.maker               = user.users
            policy.save()

            return JsonResponse({"message":"SUCCESS"}, status = 200)
        except KeyError:
            return JsonResponse({"error":"KEYERROR"}, status = 401)
        except ValueError:
            return JsonResponse({"message":"ValueError"}, status = 401)


class FundMakerView(View):
    @login_decorator
    def get(self, request):
        return JsonResponse({"data":list(FundMaker.objects.values())}, status = 200)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user = request.user
        data = json.loads(request.body)
        makers = FundMaker.objects.get(maker = user.users.id)

        try :
            makers.company_name        = data['company_name']
            makers.cs_email            = data['cs_email']
            makers.cs_number           = data['cs_number']
            makers.ceo_name            = data['ceo_name']
            makers.ceo_email           = data['ceo_email']
            makers.kakao_id            = data['kakao_id']
            makers.kakao_link          = data['kakao_link']
            makers.hompage             = data['hompage']
            makers.sns1                = data['sns1']
            makers.sns2                = data['sns2']
            makers.sns3                = data['sns3']
            makers.maker               = user.users
            makers.save()

            return JsonResponse({"message":"SUCCESS"}, status = 200)

        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)
        except ValueError:
            return JsonResponse({"message":"ValueError"}, status = 401)


class FundProjectView(View):
    def get(self, request):
        data = list(FundProject.objects.values())
        return JsonResponse({"data":data}, status=200)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user = request.user
        try :
            if FundProject.objects.filter(maker = user.users).exists():
                return JsonResponse({"MESSSAGE":"PROJECT_ALREADY_EXIST"}, status=401)
            else :
                document            = Document.objects.get(id = 1)
                main_agreement      = FundMainAgreement.objects.create(is_commision_agreed = False, is_futureopen_agreed = False, document = document, maker = user.users)
                fund_category       = FundCategory.objects.get(id = 1)
                main_information    = FundMainInformation.objects.create(is_adult_agreed = False, category = fund_category, maker = user.users)
                policy_document     = PolicyDocument.objects.get(id = 1)
                fund_policy         = FundPolicy.objects.create(q1 = True, document = policy_document, maker = user.users)
                fund_maker          = FundMaker.objects.create(company_name = True, maker = user.users)
                fund_story          = FundStory.objects.create(maker = user.users)
                five = FundProject.objects.create(
                        fund_main_agreement      = main_agreement,
                        fund_main_information    = main_information,
                        fund_policies            = fund_policy,
                        fund_makers              = fund_maker,
                        fund_story               = fund_story,
                        maker                    = user.users
                )
            return JsonResponse({"MESSAGE":"SUCCESS"}, status=200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)
        except ValueError:
            return JsonResponse({"message":"ValueError"}, status = 401)


class RewardView(View):
    @login_decorator
    def get(self, request):
        user          = request.user
        data = list(FundReward.objects.filter(maker = user.users).values())
        return JsonResponse({"data":data}, status=200)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user          = request.user
        data          = json.loads(request.body)

        try:
            FundReward.objects.filter(maker = user.users).delete()
            print(data["data"])
            fund_rewards = [
                FundReward(
                    seller_product_number = count,
                    name                  = data['name'],
                    price                 = data['price'],
                    introduction          = data['introduction'],
                    stock                 = data['stock'],
                    scheduled_date        = data['scheduled_date'],
                    option                = data['option'],
                    maker                 = user.users,
                    project               = FundProject.objects.get(maker = user.users)
            ) for count, data in enumerate(data["data"], 1)]

            FundReward.objects.bulk_create(fund_rewards)

            return JsonResponse({"MESSAGE":"SUCCESS"}, status=200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)
        except ValueError:
            return JsonResponse({"message":"ValueError"}, status = 401)

class StoryMainImage(View):
    @transaction.atomic
    @login_decorator
    def post(self, request):
        if not request.FILES['photo']:
            return JsonResponse({"MESSAGE" : "DOES_NOT_EXIST_FILE"}, status=404)
        try:
            user = request.user
            fund_story = FundStory.objects.get(maker=user.users)
            fund_info  = FundMainInformation.objects.get(maker=user.users)
            if len(request.FILES['photo'])>=2:
                for file in request.FILES.getlist('photo'):
                    file_name = str(user.id)+"-"+file.name
                    aws_s3.upload_fileobj(
                        file,
                        "wedizstoryimage",
                        file_name,
                        ExtraArgs={
                            "ContentType" : request.FILES['photo'].content_type
                        }
                    )
                    photo_url = "https://s3.ap-northeast-2.amazonaws.com/wedizstoryimage"+"-"+file_name
                    StoryPhoto(photo = photo_url, fund_story=fund_story).save()
                urls = f"""https://s3.ap-northeast-2.amazonaws.com/wedizstoryimage-{str(user.id)}-{request.FILES.getlist('photo')[0].name}"""
                fund_info.main_image = urls
                fund_info.save()
                return JsonResponse({"MESSAGE" : "SUCCESS"}, status=200)
            else:
                file_name = str(user.id)+"-"+request.FILES['photo'].name
                self.aws_s3.upload_fileobj(
                    request.FILES['photo'],
                    "wedizstoryimage",
                    file_name,
                    ExtraArgs={
                        "ContentType" : request.FILES['photo'].content_type
                    }
                )
                photo_url = "https://s3.ap-northeast-2.amazonaws.com/wedizstoryimage"+file_name
                StoryPhoto(photo = photo_url, fund_story=fund_story).save()
                fund_info.main_image = photo_url
                fund_info.save()
                return JsonResponse({"MESSAGE" : "SUCCESS", "photo_url" : photo_url}, status=200)
        except KeyError:
            return JsonResponse({"MESSSAGE" : "INVALID_INPUT"}, status=401)

class FundStoryView(View):
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        try:
            fund_story = FundStory.objects.get(maker=request.user.users)
            fund_story.summary    = data['summary']
            fund_story.is_agreed  = data['is_agreed']
            fund_story.context    = data['context']
            fund_story.maker      = request.user.users
            fund_story.save()

            return JsonResponse({"MESSAGE" : "SUCCESS"}, status=200)
        except KeyError:
            return JsonResponse({"MESSAGE" : "INVALID_INPUT"}, status=401)

    @login_decorator
    def get(self, request):
        story = FundStory.objects.get(maker=request.user.users)
        photos = list(StoryPhoto.objects.filter(fund_story=story.id).values())
        data = {
            "summary"      : story.summary,
            "is_agreed"    : story.is_agreed,
            "context"      : story.context,
            "photo"        : [ photo for photo in photos]  
        }
        return JsonResponse({ "data" : data}, status=200)
