from GoCqhttpService import go_cqhttp_service
from flask import *
from CtfVcalendar import ctf_vcalendar
from CommandParse import CommandParse
import json

# 对象创建
app = Flask(__name__)
go_cqhttp = go_cqhttp_service("http://127.0.0.1:5700")
parse = CommandParse()

ctfCaldendar = ctf_vcalendar()


@parse("group /bot info")
def get_event_detail(*args, **kwargs):
    if len(args) < 1 or not args[0].isdigit(): return "参数错误"
    return ctfCaldendar.event_detail(int(args[0], 10))


@parse("group /bot; group /bot show")
def get_recent_event(*args, **kwargs):
    return ctfCaldendar.event_summary()


@app.route("/event", methods = ["POST", "GET"])
def msg_event():
    data = json.loads(request.data)
    message_type = data["message_type"]
    from_where = data["group_id" if message_type == "group" else "user_id"]

    if len(data["message"]) != 1: return "illegal message"

    commandline = data["message"][0]["data"]["text"]
    commandline += "group " if message_type == "group" else "private " # 标记消息接入类型

    respone = parse(commandline)
    
    if respone is not None:
        go_cqhttp.send_msg(respone, message_type, from_where)
        return "done"
    else:
        return "error or no response"


if __name__ == "__main__":
    ctfCaldendar.job(sorted=True)
    app.run()
    print(parse.command_search("group /bot info"))
    
    