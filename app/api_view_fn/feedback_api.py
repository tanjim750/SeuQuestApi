from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from app.models import Conversation

class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        con_id = request.POST.get('id',None) # conversation id
        feedback = request.POST.get('rating',None) # conversation feedback as rating
        description = request.POST.get('description',None)

        if con_id is None:
            return Response({"status":"Failed","details": "Required parameter missing.","parameter":"id"}, status=status.HTTP_400_BAD_REQUEST)
        if feedback is None:
            return Response({"status":"Failed","details": "Required parameter missing.","parameter":"rating"}, status=status.HTTP_400_BAD_REQUEST)
        
        get_con = Conversation.objects.filter(user = request.user, id=con_id)

        if not get_con.exists():
            return Response({"status":"Failed","details": "User or id not exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            get_con = get_con.first()
            get_con.feedback = feedback
            get_con.description = description
            get_con.save()
        return Response({"status": "Ok","human":get_con.human_query,"bot":get_con.bot_response,"id":get_con.id,"rating":get_con.feedback,"description":get_con.description,"metadata":get_con.metadata,}, status=status.HTTP_200_OK)