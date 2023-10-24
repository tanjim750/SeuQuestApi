# appname/urls.py
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView,TokenVerifyView

urlpatterns = [
    path('addUser', views.addUser),
    path("addMessage",views.userMessage),
    path("addFeedback",views.addFeedback),
    path("retrieveMessage",views.retrieveMessage),
    path("isUserTrainer",views.isUserTrainer),
    path("userConversationMode",views.userConversationMode),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('chat/',views.ChatView.as_view(), name='chat'),
    path('chat-feedback/',views.FeedbackView.as_view(), name='feedback'),
    path('retrain-bot/',views.RetrainView.as_view(), name='retrain'),
    path('train-bot/',views.TrainView.as_view(), name='train'),

]
