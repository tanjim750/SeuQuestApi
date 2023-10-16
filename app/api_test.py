import requests,json

url = "http://127.0.0.1:8000/api/addMessage"
metadata = {"must":{"k":["cmn"]},"should":{"data_for":["hist"]}}
datas = {
    "userId":234255,
    "msgId":854,
    "human_query":"who are you",
    "bot_response":"You can call me SeuQuest",
    "metadata":json.dumps(metadata)
}
r = requests.post(url,data=datas)
print(r.json())