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
        data          = list(Order.objects.filter(user = user))

        try :
            basket = [
                {   
                    "user_name"             : result.user.user_name,
                    "phone_number"          : result.user.phone_number,
                    "email"                 : result.user.email,
                    "name"                  : result.reward.name,
                    "price"                 : result.reward.price,
                    "delivery_fee"          : result.reward.delivery_fee,
                    "scheduled_date"        : result.reward.scheduled_date,
                    "option"                : result.reward.option,
                    "delivery_name"         : result.delivery_name,
                    "delivery_number"       : result.delivery_number,
                    "delivery_address"      : result.delivery_address,
                    "delivery_request"      : result.delivery_request,
                    "card_number"           : result.card_number,
                    "card_period"           : result.card_period,
                    "card_password"         : result.card_password,
                    "card_birthday"         : result.card_birthday
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
                    reward                  = FundReward.objects.prefetch_related('basket_reward').get(id = data['reward']),
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
            a = Order.objects.bulk_create(order_info)
            for count in a:
                for data in FundReward.objects.select_for_update().filter(id = count.reward.id):
                    ordered_item = Order.basket.get_queryset(user = user)
                    for ordered_items in ordered_item:
                        data.stock = ordered_items.rewards.stock - ordered_items.quantity
            data.save()

            Basket.objects.filter(user = user).delete()

            return JsonResponse({"MESSAGE":"SUCCESS"}, status=200)
        except KeyError:
            return JsonResponse({"error":"KeyError"}, status = 401)
