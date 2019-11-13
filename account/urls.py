from django.urls import path
from .views      import (
                        SignupView,
                        SigninView,
                        ModifiedUserInfo,
                        ModifiedUserPhoto,
                        MakerCreate,
                        )
urlpatterns = [
	path('/signup', SignupView.as_view()),
	path('/signin', SigninView.as_view()),
	path('/modifyprofilephoto', ModifiedUserPhoto.as_view()),
	path('/modifyprofile', ModifiedUserInfo.as_view()),
    path('/maker', MakerCreate.as_view()),
]

