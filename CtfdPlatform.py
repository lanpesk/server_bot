import requests as pyrequests
import json
from datetime import datetime
import functools
from info import *


class RequestsError(Exception):
    def __init__(self, reson, status_code):
        self.reson = reson
        self.status_code = status_code

    def __str__(self):
        return self.reson

class CTFd:
    def __init__(self, url, access_token):
        """
        创建与CTFd平台交互类
        :param url: 平台地址
        :param access_token: 用户token,必须为admin token
        """
        self.api_access_point = f"{url}/api/v1"
        self.header = {"Authorization": f"Token {access_token}", "Content-Type": "application/json"}
        self.event_running = False
        self.user_mode = None
        self.paused = False
        self.get_competition_stats()


    def __interactive(self, api_name):
        """
        API交互操作
        :param api_name: 需要交互的api名称，例如"/challenges"，或者具体的"challenges/{challenge_id}/solves"等。
        :return: 如果请求成功将返回对应api的data返回数据。
        """

        api = self.api_access_point + api_name

        try:
            response = pyrequests.get(api, headers=self.header, timeout=2)
            if response.status_code != 200:
                raise RequestsError(f"Request faild, status code: {respone.status_code}", respone.status_code)
        except (RequestsError, pyrequests.Timeout) as e:
            print(info(e, MSG_ERROR))
            return

        response_json = json.loads(response.text)
        if not response_json["success"]:
            print(info(response_json["errors"], MSG_ERROR))
            return

        return response_json["data"]


    # this need admin user
    def get_competition_stats(self):
        """
        获取当前赛事状态
        :return: None
        """

        configs = self.__interactive("/configs")
        if configs is None: return

        time_configs = list(filter(
            lambda x:x['key'] in ["start", "end"],
            configs
        ))

        start = None
        end = None

        for i in time_configs:
            if i['key'] == 'end' and i['value'] != '':
                end = datetime.fromtimestamp(int(i['value']))
            if i['key'] == 'start' and i['value'] != '':
                start = datetime.fromtimestamp(int(i['value']))

        now =  datetime.now()
        if end is None: self.event_running = True
        else :
            if now < end and (
                start is None or start < now
            ) :
                self.event_running = True
            else :
                self.event_running = False

        for i in configs:
            if i["key"] == "user_mode":
                self.user_mode == i["value"]
                break

        for i in configs:
            if i['key'] == 'paused':
                self.paused = True if i['value'] == "1" else False
                break

    def get_scoreboard(self):
        """
        获取scoreboard
        :return: scoreboard: list[dict]
        """
        return self.__interactive("/scoreboard")


    def print_scoreboard(self):
        """
        打印scoreboard
        :return: str
        """
        table = self.get_scoreboard()

        if table is None or table == []: return

        response = []

        for user in table[:10]:
            response.append(
                ljust(f"{user['pos']}", 6) + ljust(f"{user['score']}", 10) + f"{user['name']}"
            )

        return "ScoreBoard\n"    \
               "---------------\n" + \
               "pos:".ljust(6) + "score:".ljust(10) + "user or team:\n" + \
               "\n".join(response)


    def get_challenges(self):
        """
        获取题目列表
        :return: list[dict]
        """
        return self.__interactive("/challenges")


    def get_specific_challenge(self, challenge_id):
        return self.__interactive(f"/challenges/{challenge_id}")


    def print_challenges(self):
        challenges = self.get_challenges()

        if challenges is None or challenges == []: return

        response = []
        for index, chall in enumerate(challenges):
            response.append(
                ljust(f"{chall['id']}", 7) + ljust(f"{chall['category']}", 10) + ljust(f"{chall['solves']}", 7) + f"{chall['name']}"
            )
        return "Challenges\n"    \
               "---------------\n" + \
               f"id:".ljust(7) + f"type:".ljust(10) + f"solves:".ljust(10) + f"name:\n" +\
               "\n".join(response)


    def get_solve(self, challenge_id):
        """
        获取解出列表
        :param challenge_id: 指定题目id
        :return:
        """
        return self.__interactive(f"/challenges/{challenge_id}/solves")


    def print_specific_chall_solve(self, challenge_id, *args):
        solves = self.get_solve(challenge_id)[:10]

        if solves is None or solves == []: return

        response = []
        for index, solve in enumerate(solves):
            response.append(
                f"{index + 1}".ljust(8) + f"{solve['name']}"
            )

        if len(args) != 0: challenge_name = args[0]
        else:
            challenge_name = self.get_specific_challenge(challenge_id)["name"]

        return f"{challenge_name} solvers\n" +\
               "---------------\n" + \
               "pos:".ljust(8) + "user or team:\n" + \
               "\n".join(response)


    def print_specific_chall_solve_by_name(self, challenge_name):
        challenges = self.get_challenges()

        if challenges is None or challenges == []: return

        for i in challenges:
            if i["name"] == challenge_name:
                return self.print_specific_chall_solve(i['id'])
        return

    @staticmethod
    def first_kill(data):
        response = None
        if data["place"] == 1: response = f"恭喜 {data['user']} 获得 {data['chall']} 一血！"
        if data["place"] == 2: response = f"恭喜 {data['user']} 获得 {data['chall']} 二血！"
        if data["place"] == 3: response = f"恭喜 {data['user']} 获得 {data['chall']} 三血！"
        return response


if __name__=="__main__":
    ctfd = CTFd(
        "http://127.0.0.1:4000",
        "18a1506dcd69fb549a3d0955620e36d71730062cca378a60d21fd107f376211f",
    )
    # print(ctfd.print_challenges())
    # print(ctfd.print_scoreboard())
    # print(ctfd.print_specific_chall_solve(1))
    print(ctfd.print_specific_chall_solve_by_name("123213"))