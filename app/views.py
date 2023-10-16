from django.http import JsonResponse
from .models import User,Feedback,ConversationMode
from django.views.decorators.csrf import csrf_exempt

import json

@csrf_exempt
def addUser(request):
    required_parameters = {"userId":"Required","firstName":"Required","lastName":"Optional"}
    try:
        if request.method == 'POST':
            print(request.POST)
            userId = request.POST.get('userId', None)
            firstName = request.POST.get('firstName', None)
            lastName = request.POST.get('lastName', None)

            if userId and firstName and lastName:
                user_exist = User.objects.filter(userId=userId).exists()
                if not user_exist:
                    user = User(userId=userId, firstName=firstName, lastName=lastName)
                    user.save()
                    result = "New user added"
                    id = user.id

                    # Add user conversation mode 
                    ConversationMode.objects.create(user=user,mode="general")
                else:
                    result = "User Already exists"
                
                return JsonResponse({"status":200,"success": True,'response': result,})
            else:
                return JsonResponse({"status":400,"success": False,'error': "Required parameters missing","required_parameters":json.dumps(required_parameters)})
        else:
            return JsonResponse({"status":400,"success": False,'error': "This an invalid requests.",})
    except:
        return JsonResponse({"status":400,"success": False,'response': "Unknown",})

@csrf_exempt
def isUserTrainer(request):
    required_parameters = {"userId":"Required"}
    try:
        if request.method == "GET":
            userId = request.GET.get('userId',None)
            if userId:
                user = User.objects.filter(userId=userId).first()
                if user:
                    is_trainer = user.is_trainer
                    return JsonResponse({"status":200,"success": True,'is_trainer': is_trainer,"user_id":user.userId})
                else:
                    return JsonResponse({"status":400,"success": False,'error': "User not found"})
            else:
                return JsonResponse({"status":400,"success": False,'error': "Required parameters missing","required_parameters":json.dumps(required_parameters)})
        else:
            return JsonResponse({"status":400,"success": False,'error': "This an invalid requests.",})
    except Exception as e:
        return JsonResponse({"status":400,"success": False,'error': str(e)})

@csrf_exempt
def userConversationMode(request):
    print(request.method)
    try:
        if request.method == "POST":
            required_parameters = {"userId":"Required","mode":"Required"}
            userId = request.POST.get('userId',None)
            mode = request.POST.get('mode',None)
            
            if userId and mode:
                user = User.objects.filter(userId=userId).first()
                if user:
                    conversation_obj = ConversationMode.objects.filter(user=user).first()
                    if conversation_obj:
                        conversation_obj.mode = mode
                        conversation_obj.save()
                        return JsonResponse({"status":200,"success": True,'mode': conversation_obj.mode,"user_id":conversation_obj.user.userId})
                    else:
                        return JsonResponse({"status":400,"success": False,'error': "No conversation found for the user","user_id":conversation_obj.user.userId})
                else:
                    return JsonResponse({"status":400,"success": False,'error': "User not found"})
            else:
                return JsonResponse({"status":400,"success": False,'error': "Required parameters missing","required_parameters":json.dumps(required_parameters)})
            
        elif request.method == "GET":
            required_parameters = {"userId":"Required"}
            userId = request.GET.get('userId',None)
            print(request.GET)
            if userId:
                user = User.objects.filter(userId=userId).first()
                if user:
                    conversation_obj = ConversationMode.objects.filter(user=user).first()
                    if conversation_obj:
                        mode = conversation_obj.mode
                        return JsonResponse({"status":200,"success": True,'mode': mode,"user_id":conversation_obj.user.userId})
                    else:
                        return JsonResponse({"status":400,"success": False,'error': "No conversation found for the user","user_id":conversation_obj.user.userId})
                else:
                    return JsonResponse({"status":400,"success": False,'error': "User not found"})
            else:
                return JsonResponse({"status":400,"success": False,'error': "Required parameters missing","required_parameters":json.dumps(required_parameters)})
            
        else:
            return JsonResponse({"status":400,"success": False,'error': "This an invalid requests.",})
    except Exception as e:
        return JsonResponse({"status":400,"success": False,'error': str(e)})
    
@csrf_exempt   
def userMessage(request):
    required_parameters = {"userId":"Required","msgId":"Required","human_query":"Required","bot_response":"Required","metadata":"Required"}
    try:
        if request.method == "POST":
            userId = request.POST.get('userId',None)
            msgId = request.POST.get('msgId',None)
            human_query = request.POST.get('human_query',None)
            bot_response = request.POST.get('bot_response',None)
            metadata = request.POST.get('metadata',None)
            
            if userId and msgId and bot_response and human_query and metadata:
                user = User.objects.filter(userId=userId).first()
                metadata = json.loads(metadata)
                if user:
                    obj = Feedback(user=user, msgId=msgId,human_query=human_query, bot_response=bot_response,metadata=metadata)
                    obj.save()
                    return JsonResponse({"status":200,"success": True,'response': "New message added successfully","id":obj.id})
                else:
                    return JsonResponse({"status":400,"success": False,'error': "User not found"})
            else:
                return JsonResponse({"status":400,"success": False,'error': "Required parameters missing","required_parameters":json.dumps(required_parameters)})
        else:
            return JsonResponse({"status":400,"success": False,'error': "This an invalid requests.",})
    except:
        return JsonResponse({"status":400,"success": False,'error': "Unknown"})

@csrf_exempt   
def addFeedback(request):
    required_parameters = {"userId":"Required","msgId":"Required","feedback":"Required"}
    try:
        if request.method == "POST":
            userId = request.POST.get('userId',None)
            msgId = request.POST.get('msgId',None)
            feedback = request.POST.get('feedback',None)

            if userId and msgId and feedback:
                user = User.objects.filter(userId=userId).first()
                if user:
                    msg = Feedback.objects.filter(user=user,msgId=msgId).first()
                    if msg:
                        msg.feedback = feedback
                        msg.save()
                        return JsonResponse({"status":200,"success": True,'response': "Feedback successfully added","id":msg.id})
                    else:
                        return JsonResponse({"status":400,"success": False,'error': "Message id not found"})
                else:
                    return JsonResponse({"status":400,"success": False,'error': "User not found"})
            else:
                return JsonResponse({"status":400,"success": False,'error': "Required parameters missing","required_parameters":json.dumps(required_parameters)})
        else:
            return JsonResponse({"status":400,"success": False,'error': "This an invalid requests.",})
    except Exception as e:
        return JsonResponse({"status":400,"success": False,'error': str(e)})
    

@csrf_exempt
def retrieveMessage(request):
    required_parameters = {"userId":"Required","msgId":"Required"}
    try:
        if request.method == "GET":
            userId = request.GET.get('userId',None)
            msgId = request.GET.get('msgId',None)

            if userId and msgId :
                user = User.objects.filter(userId=userId).first()
                if user:
                    msg = Feedback.objects.filter(user=user,msgId=msgId).first()
                    if msg:
                        bot_response = msg.bot_response
                        human_query = msg.human_query
                        metadata = msg.metadata
                        return JsonResponse({"status":200,"success": True,'human_query': human_query,"bot_response":bot_response,"metadata":metadata,"id":msg.id})
                    else:
                        return JsonResponse({"status":400,"success": False,'error': "Message id not found"})
                else:
                    return JsonResponse({"status":400,"success": False,'error': "User not found"})
            else:
                return JsonResponse({"status":400,"success": False,'error': "Required parameters missing","required_parameters":json.dumps(required_parameters)})
        else:
            return JsonResponse({"status":400,"success": False,'error': "This an invalid requests.",})
    except Exception as e:
        return JsonResponse({"status":400,"success": False,'error': str(e)})

