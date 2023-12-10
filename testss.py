types = {"Message_Private_Collection": {
        "name": "example name",
        "messages": {
            "sender": "sender",
            "receiver": "receiver",
            "status": 1,
            "sending_time": "2020-10-15 23:59:59",
            "deleted_by_owner": False,
            "extera": [{"like": None}, {"smile": None}]
        }
    }
}

tests = {
            "sender": "sendersender",
            "receiver": "reciverreciver",
            "status": 2,
            "sending_time": "2020-10-15 23:59:59",
            "deleted_by_owner": True,
            "extera": [{"like": None}, {"smile": None}]
        }
print(types)
asswess = types.get("Message_Private_Collection").get("messages") | tests
print(asswess)
