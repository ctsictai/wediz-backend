from django.urls import path
from .views      import BasketView, OrderView
urlpatterns = [
	path('/basket', BasketView.as_view()),
	path('', OrderView.as_view()),
]

