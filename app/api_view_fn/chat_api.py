from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

import json
from qdrant_client.http import models as qdrant_models
from transformers import AutoTokenizer, AutoModel
import torch
import random

from Seuquest_bot import SeuQuest
from app.models import Conversation

qdrant_url="https://7a70d684-542d-4bd3-adb9-04eb7640dc00.us-east-1-0.aws.cloud.qdrant.io:6333"
qdrant_api = "cWv31u7XIINmOYuPbxwvmwTslOJU85o8BXsc2vt3A_pI-3ie_0mZIw"

seu_quest = SeuQuest()
# seu_quest.Faiss(seu_quest,"/media/tanjim/Tanjim/python/AI/NLP/seuquest/vectors/vectorstore").load()
qdrant = seu_quest.QDRANT(instance=seu_quest,url=qdrant_url,api_key=qdrant_api)
qdrant.load(collection_name="DataStore")

def generate_answer(query,metadatas:dict):
    try:
        answer = seu_quest.generate_answer(question=query,metadatas=metadatas)

        # Sentiment recognition
        # from transformers import pipeline
        # sentiment_analyzer = pipeline("sentiment-analysis")
        # sentiment = sentiment_analyzer(answer)
        # sentiment_label = sentiment[0]['label']
        # sentiment_score = int(sentiment[0]['score']*100)
        return answer
    except Exception as e:
        return None

def get_metadata(con_mode,query):
    metadatas = {}
    try:
        con_mode = "hist" if con_mode == "general" else con_mode
        if con_mode == "hist":
                metadatas = {"must":{"k":["cmn"]},"should":{"data_for":["hist"]}}
                
                if "cse" in query.lower() or "computer science" in query.lower():
                    metadatas["should"]["data_for"].append("cse_dept")
                if "eee" in query.lower() or "electrical and electronics" in query.lower():
                    metadatas["should"]["data_for"].append("eee_dept")
                if "pharmacy" in query.lower():
                    metadatas["should"]["data_for"].append("pharmacy_dept")
                if "textile" in query.lower():
                    metadatas["should"]["data_for"].append("textile_dept")
                if "architecture" in query.lower():
                    metadatas["should"]["data_for"].append("architecture_dept")
                if "bba" in query.lower() or "business administration" in query.lower():
                    metadatas["should"]["data_for"].append("bba_dept")
                if "law" in query.lower():
                    metadatas["should"]["data_for"].append("law_dept")
                if "english" in query.lower():
                    metadatas["should"]["data_for"].append("english_dept")
                if "bangla" in query.lower():
                    metadatas["should"]["data_for"].append("bangla_dept")
                if "mds" in query.lower() or "development studies" in query.lower():
                    metadatas["should"]["data_for"].append("mds_dept")
                if "notices" in query.lower():
                    metadatas["should"]["data_for"].append("notices")
                if "admission" in query.lower():
                    metadatas["should"]["additional"].append("admission")
                if "scholarship" in query.lower() or "waiver" in query.lower():
                    metadatas["should"]["additional"].append("admission")
                
        else:
            depts = ["cse_dept","eee_dept","pharmacy_dept","textile_dept","architecture_dept",
                            "bba_dept","law_dept","english_dept","bangla_dept","economics_dept","mds_dept"
                            ]
            depts.remove(con_mode)
            metadatas = {"should":{"data_for":[con_mode,"hist"]},"must_not":{"data_for":[dept_ for dept_ in depts]}}

        return metadatas
    except Exception as e:
        return metadatas


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            run = True
            while run:
                # Generate a uniqe six-digit conversation id
                con_id = ''.join([str(random.randint(0, 9)) for _ in range(6)])

                con_id_exists = Conversation.objects.filter(id=con_id).exists()
                if not con_id_exists:
                    run = False

            query = request.GET.get('query', None)
            metadatas = request.GET.get('metadatas', None)
            conversation_mode = request.GET.get('conversation_mode', None)

            if query is None:
                return Response({"status":"Failed","details": "Required parameter missing.","parameter":"query"}, status=status.HTTP_400_BAD_REQUEST)
            if conversation_mode is None:
                return Response({"status":"Failed","details": "Required parameter missing.","parameter":"conversation_mode"}, status=status.HTTP_400_BAD_REQUEST)
            if metadatas is None:
                metadatas = get_metadata(conversation_mode,query)
            bot_response = generate_answer(query, metadatas)

            # saving the conversation in the database
            con_db = Conversation.objects.create(user= request.user,id=con_id,human_query = query,bot_response=bot_response,metadata=metadatas)

            return Response({"status": "Ok","human":query,"bot":bot_response,"id":con_db.id,"rating":con_db.feedback,"description":con_db.description,"metadata":metadatas,}, status=status.HTTP_200_OK)
        except Exception as e:
            Response({"status":"server-error","details":"During the processing an error occurred"},status=501)
