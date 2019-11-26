from django.urls import path
from .views import MainInformation, MainAgreement, FundMakerView, FundPolicyView, FundProjectView, StoryMainImage, FundStoryView, RewardView

urlpatterns = [
    path('/maininfo', MainInformation.as_view()),
    path('/agreement', MainAgreement.as_view()),
    path('/policy', FundPolicyView.as_view()),
    path('/makerinfo', FundMakerView.as_view()),
    path('/project', FundProjectView.as_view()),
    path('/reward', RewardView.as_view()),
    path('/storyimage', StoryMainImage.as_view()),
    path('/story', FundStoryView.as_view())
]
