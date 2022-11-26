import requests as pyrequests
import json

class RequestsError(Exception):
    def __init__(self, reson, status_code):
        self.reson = reson
        self.status_code = status_code

    def __str__(self):
        return self.reson

class go_cqhttp_service:
    def __init__(self, go_cqhttp_url):
        self.go_cphttp_url = go_cqhttp_url

    def send_msg(self, msg, type, target):
        send_msg_header = {"Content-Type": "application/json"}
        send_msg_body = {"message_type": type,
                         "group_id" if type == "group" else "user_id": target,
                         "message": msg}

        try:
            response = pyrequests.post(self.go_cphttp_url + "/send_msg", headers=send_msg_header,
                                       data=json.dumps(send_msg_body), timeout=2)
            if response.status_code != 200:
                raise RequestsError(f"Request faild, status code: {response.status_code}", response.status_code)
        except (RequestsError, pyrequests.Timeout) as e:
            return e

        return f"Msg send: \n{msg}"