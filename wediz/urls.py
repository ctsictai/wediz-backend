from django.urls import path, include

urlpatterns = [
    path('account', include('account.urls')),
    path('fund', include('fund.urls')),
    path('order', include('order.urls')),
]
