from GoCqhttpService import go_cqhttp_service
from flask import *
from CtfVcalendar import ctf_vcalendar
from CommandParse import CommandParse
from CtfdPlatform import CTFd
from info import *
import json

# 对象创建
app = Flask(__name__)
go_cqhttp = go_cqhttp_service("http://127.0.0.1:5700")
parse = CommandParse()

ctfCaldendar = ctf_vcalendar()

url = "http://172.23.14.109"
token = "82ee12a364b3d1af2f203c90c689fa53f68f496015bd9b61c159e63fa0fff464"


@parse("group /help; private /help")
def ret_help(*args, **kwargs):
    return parse.help()


@parse("group /event info",
       help="/event info <i>: 显示第i条赛事的详细信息")
def get_event_detail(*args, **kwargs):
    if len(args) < 1 or not args[0].isdigit(): return "参数错误"
    return ctfCaldendar.event_detail(int(args[0], 10) - 1)


@parse("group /event; group /event show",
       help = "/event 或 /event show: 显示近期赛事")
def get_recent_event(*args, **kwargs):
    if len(args) != 0 or len(kwargs) != 0: return "参数错误"
    return ctfCaldendar.event_summary()


@parse("group /event help",
       help="/event help: 显示ctf日历指令信息")
def ret_event_help():
    pass


@parse("group /plat; group /plat stat",
       help="/plat 或 /plat stat: 显示平台比赛状态")
def get_comp_stat(*args, **kwargs):
    if len(args) != 0 or len(kwargs) != 0: return "参数错误"

    platform = CTFd(url, token)

    if not platform.event_running and not platform.paused:
        response = "赛事未进行"
    else:
        response = "赛事已开启，" + ("队伍模式" if platform.user_mode == "teams" else "单人模式")

    return response


@parse("group /plat score",
       help="/plat score: 显示当前积分榜")
def show_scoreboard(*args, **kwargs):
    if len(args) != 0 or len(kwargs) != 0: return "参数错误"
    platform = CTFd(url, token)
    if not platform.event_running: return "赛事未进行"
    return platform.print_scoreboard()


@parse("group /plat chall",
       help="/plat chall: 显示题目列表")
def show_chall(*args, **kwargs):
    if len(args) != 0 or len(kwargs) != 0: return "参数错误"
    platform = CTFd(url, token)
    if not platform.event_running: return "赛事未进行"
    return platform.print_challenges()


@parse('group /plat chall solve',
       help='/plat chall solve "<chall_name>": 显示指定题目的解题队伍')
def show_chall_solve(*args, **kwargs):
    platform = CTFd(url, token)
    if not platform.event_running: return "赛事未进行"

    if len(args) < 1: return "参数缺少"
    return platform.print_specific_chall_solve_by_name(args[0].replace('"', ""))


@app.route("/event", methods = ["POST", "GET"])
def msg_event():
    data = json.loads(request.data)
    message_type = data["message_type"]
    from_where = data["group_id" if message_type == "group" else "user_id"]

    if len(data["message"]) != 1: return "illegal message"

    commandline = data["message"][0]["data"]["text"]

    print(info(f"receive code: {commandline}", MSG_INFO))

    commandline = ("group " if message_type == "group" else "private ") + commandline # 标记消息接入类型

    respone = parse.command_search(commandline)

    
    if respone is not None:
        print(info(f"send response:\n{respone}", MSG_INFO))
        go_cqhttp.send_msg(respone, message_type, from_where)
        return "done"
    else:
        return "error or no response"


@app.route("/first_kill", methods = ["POST", "GET"])
def first_kill_boardcast():
    data = json.loads(request.data)

    response = CTFd.first_kill(data)

    target = ""

    print(response)
    # go_cqhttp.send_msg(respone, message_type, target)

    return response


if __name__ == "__main__":
    ctfCaldendar.job(sorted=True)
    app.run()
    
    