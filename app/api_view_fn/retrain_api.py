import json
from qdrant_client.http import models as qdrant_models
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from Seuquest_bot import SeuQuest
from app.models import Conversation

collection_name="DataStore"
qdrant_url="https://7a70d684-542d-4bd3-adb9-04eb7640dc00.us-east-1-0.aws.cloud.qdrant.io:6333"
qdrant_api = "cWv31u7XIINmOYuPbxwvmwTslOJU85o8BXsc2vt3A_pI-3ie_0mZIw"

seu_quest = SeuQuest()
qdrant = seu_quest.QDRANT(instance=seu_quest,url=qdrant_url,api_key=qdrant_api)
qdrant.load(collection_name=collection_name)

def find_highest_similarity(source_sen,compare_sen):
  sentences = [
      source_sen
  ]
  for sen in compare_sen:
    sentences.append(sen)

  model_name = 'sentence-transformers/all-MiniLM-L6-v2'
  # model_name = 'sentence-transformers/bert-base-nli-mean-tokens'

  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModel.from_pretrained(model_name)

  # initialize dictionary to store tokenized sentences
  tokens = {'input_ids': [], 'attention_mask': []}

  for sentence in sentences:
      # encode each sentence and append to dictionary
      new_tokens = tokenizer.encode_plus(sentence, max_length=128,
                                        truncation=True, padding='max_length',
                                        return_tensors='pt')
      tokens['input_ids'].append(new_tokens['input_ids'][0])
      tokens['attention_mask'].append(new_tokens['attention_mask'][0])

  # reformat list of tensors into single tensor
  tokens['input_ids'] = torch.stack(tokens['input_ids'])
  tokens['attention_mask'] = torch.stack(tokens['attention_mask'])

  outputs = model(**tokens)
  outputs.keys()

  embeddings = outputs.last_hidden_state
  embeddings.shape

  attention_mask = tokens['attention_mask']
  attention_mask.shape

  mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
  mask.shape

  masked_embeddings = embeddings * mask
  masked_embeddings.shape

  summed = torch.sum(masked_embeddings, 1)
  summed.shape

  summed_mask = torch.clamp(mask.sum(1), min=1e-9)
  summed_mask.shape

  mean_pooled = summed / summed_mask


  # convert from PyTorch tensor to numpy array
  mean_pooled = mean_pooled.detach().numpy()

  # calculate
  simiarity = (cosine_similarity(
      [mean_pooled[0]],
      mean_pooled[1:]
  )).tolist()

  similarity_scores = []

  for i,sen in enumerate(sentences[1:]):
    similarity_score = (simiarity[0][i])*100
    rounded_similarity = round(similarity_score)
    similarity_scores.append(rounded_similarity)

  height_similarity_score = max(similarity_scores)
  index_of_similar_sen = similarity_scores.index(height_similarity_score)
  return (height_similarity_score,index_of_similar_sen)

def retrain_with_new_data(query,metadata,data):
    data = SeuQuest.text_cleaner(data)
    filter_ = SeuQuest.qdrant_metadata_filtering(metadata)

    query_vector = SeuQuest.embeddings.embed_query(query)
    client = qdrant.client_
    hits = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter = filter_,
        limit=4
    )

    # the list([(24.56,1)]) contains tuple in this tuple index 0 is score and 1 is index number of the similar content
    similarity_scores = []

    for hit in hits:
        page_contents = hit.payload["page_content"].split("\n")
        sentences = []
        for content in page_contents:
            split_content = content.split(":",1)
            if len(split_content) > 1:
                sentences.append(split_content[1])
            else:
                sentences.append(split_content[0])
        score = find_highest_similarity(data,sentences)
        similarity_scores.append(score)

    # print(similarity_scores)
    height_similarity_score = max(similarity_scores)
    if height_similarity_score[0] >77:
        content_index = height_similarity_score[1]
        hit_index = similarity_scores.index(height_similarity_score)
        page_content = hits[hit_index]
        vector_point = page_content.id
        content_metadata = page_content.payload["metadata"]
        contents = page_content.payload["page_content"].split("\n")
        replace_content = contents[content_index]
        split_content = replace_content.split(":",1)

        if len(split_content) > 1:
            # print(split_content[1],"\n\n\n")
            split_content[1] = ": "+data
        else:
            split_content[0] = data

        new_content = "".join(split_content)
        contents[content_index] = new_content
        final_contents = "\n".join(contents)

        payload = {"metadata":content_metadata,"page_content":final_contents}

        qdrant.overwrite_payload(collection_name=collection_name,points=[vector_point],payload=payload)
        return True

    else:
       return False
    

# main api view
class RetrainView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        is_trainer = request.user.is_superuser
        if not is_trainer:
            return Response({"status":"Failed","details": "The user do not have the training access "}, status=status.HTTP_401_UNAUTHORIZED)

        con_id = request.POST.get('id',None) # conversation id
        data = request.POST.get('data',None) # given trainer context 
        if con_id is None:
            return Response({"status":"Failed","details": "Required parameter missing.","parameter":"id"}, status=status.HTTP_400_BAD_REQUEST)
        if data is None:
            return Response({"status":"Failed","details": "Required parameter missing.","parameter":"data"}, status=status.HTTP_400_BAD_REQUEST)
        
        get_con = Conversation.objects.filter(id=con_id)
        if not get_con.exists():
            return Response({"status":"Failed","details": "Given id does not exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        get_con = get_con.first()
        query = get_con.human_query
        metadata = get_con.metadata
        succeed = retrain_with_new_data(query,metadata,data)

        if succeed:
            return Response({"status":"OK","details": "Successfully trained on given context."}, status=status.HTTP_200_OK)
        else:
            return Response({"status":"Failed","details": "could not be trained on given context. Because given context did not provide information about your query"}, status=status.HTTP_400_BAD_REQUEST)




