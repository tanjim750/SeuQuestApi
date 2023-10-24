from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
import json

from .api_view_fn.chat_api import ChatView
from .api_view_fn.feedback_api import FeedbackView
from .api_view_fn.retrain_api import RetrainView
from .api_view_fn.train_api import TrainView



