import json
import jwt
import bcrypt
import datetime
import boto3

from django.views      import View
from django.http       import JsonResponse, HttpResponse
from django.db         import transaction

from my_settings       import WEDIZ_SECRET
from account.models    import User
from fund.models       import FundReward, FundProject

from .models           import Basket, Order
from .utils            import login_decorator

class BasketView(View):
    @login_decorator
    def get(self, request):
        user          = request.user
        data          = list(Basket.objects.select_related('rewards').filter(user = user))
        try :
            basket = [
                {   "id"            : result.id,
                    "name"          : result.rewards.name,
                    "product_id"    : result.rewards.id,
                    "price"         : result.rewards.price,
                    "quantity"      : result.quantity,
                    "sponser"       : result.sponser,
                    "delivery_fee"  : result.rewards.delivery_fee,
                    "user_name"     : result.user.user_name,
                    "email"         : result.user.email,
                    "phone_number"  : result.user.phone_number
                }
            for result in data ]
            return JsonResponse({"data":basket}, status=200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user           = request.user
        data           = json.loads(request.body)

        try:
            fund_project = FundProject.objects.prefetch_related('fundrewards').get(id = data["data"][0]['project_id'])
            basket_info = [
                Basket(
                    rewards               = FundReward.objects.get(id = data['id']),
                    project               = fund_project,
                    user                  = user,
                    sponser               = data['sponser'],
                    stock                 = data['stock'],
                    quantity              = data['quantity']
                    ) for data in data["data"]]
            Basket.objects.bulk_create(basket_info)

            return JsonResponse({"MESSAGE":"SUCCESS"}, status=200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)

class OrderView(View):
    @login_decorator
    def get(self, request):
        user          = request.user
        data          = list(Order.objects.prefetch_related('basket').filter(user = user))
        try :
            basket = [
                {   
                    "user"          : result.name,
                    "basket"         : result.basket.id,
                    "delivery_name"      : result.quantity,
                    "delivery_number"       : result.sponser,
                    "delivery_address"  : result.rewards.delivery_fee,
                    "delivery_request"     : result.user.user_name,
                    # "card_number"         : result.user.email,
                    # "card_period"          : result.name,
                    # "basket"         : result.basket.sponser,
                    # "delivery_name"      : result.quantity,
                    # "delivery_number"       : result.sponser,
                    # "delivery_address"  : result.rewards.delivery_fee,
                    # "delivery_request"     : result.user.user_name,
                    "email"         : result.user.email,

                    "phone_number"  : result.user.phone_number
                }
            for result in data ]
            return JsonResponse({"data":basket}, status=200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        user           = request.user
        data           = json.loads(request.body)

        try:
            order_info = [
                Order(
                    user                    = user,
                    basket                  = Basket.objects.get(id = data['id']),
                    is_support_agreed       = data['is_support_agreed'],
                    delivery_name           = data['delivery_name'],
                    delivery_number         = data['delivery_number'],
                    delivery_address        = data['delivery_address'],
                    delivery_request        = data['delivery_request'],
                    card_number             = data['card_number'],
                    card_period             = data['card_period'],
                    card_password           = data['card_period'],
                    card_birthday           = data['card_birthday'],
                    is_agreed               = data['is_agreed']
                    ) for data in data["data"]]
            Order.objects.bulk_create(order_info)

            ordered_item = Basket.objects.filter(user = user)
            minus_stock= [ 
                Basket(                                   )
            for data in ordered_item]

            return JsonResponse({"MESSAGE":"SUCCESS"}, status=200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)
