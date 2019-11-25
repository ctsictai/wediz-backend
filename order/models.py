from django.db      import models
from fund.models    import FundReward, FundProject
from account.models import User


class Basket(models.Model):
    sponser        = models.IntegerField(null=True)
    stock          = models.IntegerField(null=True)
    quantity       = models.IntegerField(null=False)
    rewards        = models.ForeignKey(FundReward,  on_delete = models.CASCADE, related_name="basket_reward")
    project        = models.ForeignKey(FundProject, on_delete = models.CASCADE, related_name="basket_project") 
    user           = models.ForeignKey(User,        on_delete = models.CASCADE, related_name="basket_user")

    class Meta:
        db_table = "baskets"


class Order(models.Model):
    is_support_agreed       = models.BooleanField(null=True)
    delivery_name           = models.CharField(max_length=10,  null = True)
    delivery_number         = models.CharField(max_length=12,  null = True)
    delivery_address        = models.CharField(max_length=100, null = True)
    delivery_request        = models.CharField(max_length=20,  null = True)
    card_number             = models.CharField(max_length=4,   null = True)
    card_period             = models.CharField(max_length=10,  null = True)
    card_password           = models.CharField(max_length=2,   null = True)
    card_birthday           = models.CharField(max_length=10,  null = True)
    is_agreed               = models.BooleanField(null = True)
    basket                  = models.ForeignKey(Basket, on_delete =models.SET_NULL, related_name="orders", null = True)
    user                    = models.ForeignKey(User, on_delete = models.CASCADE, related_name="Order.user+")
    reward                  = models.ForeignKey(FundReward, on_delete = models.CASCADE, related_name="reward")
    class Meta:
        db_table  = "orders"