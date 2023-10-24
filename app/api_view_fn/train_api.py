from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from Seuquest_bot import SeuQuest

collection_name="DataStore"
qdrant_url="https://7a70d684-542d-4bd3-adb9-04eb7640dc00.us-east-1-0.aws.cloud.qdrant.io:6333"
qdrant_api = "cWv31u7XIINmOYuPbxwvmwTslOJU85o8BXsc2vt3A_pI-3ie_0mZIw"

seu_quest = SeuQuest()
qdrant = seu_quest.QDRANT(instance=seu_quest,url=qdrant_url,api_key=qdrant_api)
qdrant.load(collection_name=collection_name)

# main api view
class TrainView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            is_trainer = request.user.is_superuser
            if not is_trainer:
                return Response({"status":"Failed","details": "The user do not have the training access "}, status=status.HTTP_401_UNAUTHORIZED)

            data = request.POST.get('data',None) # given trainer context 
            conversation_mode = request.GET.get('conversation_mode', None)
            if conversation_mode is None:
                return Response({"status":"Failed","details": "Required parameter missing.","parameter":"conversation_mode"}, status=status.HTTP_400_BAD_REQUEST)
            if data is None:
                return Response({"status":"Failed","details": "Required parameter missing.","parameter":"data"}, status=status.HTTP_400_BAD_REQUEST)

            metadata = {"k": "cmn","data_for": conversation_mode}
            qdrant.train(data,metadata)
            return Response({"status":"OK","details": "Successfully trained on given context."}, status=status.HTTP_200_OK)
        except:
            Response({"status":"server-error","details":"During the processing an error occurred"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)