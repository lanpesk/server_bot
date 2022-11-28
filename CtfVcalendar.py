import requests
import json
import time
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

class QueryEventFaild(Exception):
    def __init__(self, reason, code):
        self.reason = reason
        self.code = code

    def __str__(self):
        return self.reason

class ctf_vcalendar:
    def __init__(self):
        self.api = "https://api.ctfhub.com/User_API/Event/getAllICS"
        self.raw_data = None
        self.parse_data = None

        # 创建每日获取赛事的定时事件
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.scheduler.add_job(self.job, trigger='cron', hour=8, minute=0, second=0, timezone='Asia/Shanghai')


    def job(self, sorted = False):
        print("update caldendar")
        self.query_event()
        self.parse(sorted=sorted)


    def query_event(self):
        """
        获取日程， 注意会抛出异常
        :return: 无
        """
        response = requests.get(self.api, verify=r"api.crt")
        if response.status_code != 200:
            raise QueryEventFaild(f"Request for api faild, status code : {response.status_code}")
        self.raw_data = response.text


    def parse(self, sorted = False):
        """
        对获取到的数据进行解析
        sorted: 是否按照开始时间排序，默认是按照结束时间排序
        :return:
        """
        if self.raw_data is None:
            return False
        lines = self.raw_data.splitlines()

        # VCALENDAR格式判断。
        if lines[0] != "BEGIN:VCALENDAR" or lines[-1] != "END:VCALENDAR":
            return False
        if "BEGIN:VEVENT" not in lines or "END:VEVENT" not in lines:
            return False

        def vevent_filter(data: list):
            try:
                start = data.index("BEGIN:VEVENT")
                end = data.index("END:VEVENT")
                event = data[start:end+1]
            except:
                return

            while True:
                yield event
                try:
                    start = data.index("BEGIN:VEVENT", end+1)
                    end = data.index("END:VEVENT", end + 1)
                    event = data[start:end + 1]
                except:
                    return

        parse_data = []

        for event in vevent_filter(lines):
            sub = []
            for index in range(len(event)):
                if event[index].startswith(" "):
                    event[index-1] += event[index][1:]
                    sub.append(index)
            sub.reverse()
            for index in sub:
                event.pop(index)

            dict_data = {}
            for i in event[1:-1]:
                split = i.index(":")
                key = i[:split]
                data = i[split+1:]
                dict_data[key] = data

            parse_data.append(dict_data)

        # DESCRIPTION 解析
        for index in range(len(parse_data)):
            parse_data[index]["DESCRIPTION"] = parse_data[index]["DESCRIPTION"].split(" | ")

        # DTSTART DTEND 解析
        expired = []

        tz = pytz.timezone("Asia/Shanghai")
        utc = pytz.timezone('UTC')

        timestamp = self.get_localtime()
        if timestamp is not None:
            localtime = datetime.fromtimestamp(int(timestamp)).astimezone(tz)
        else:
            localtime = datetime.now().astimezone(utc)

        for index in range(len(parse_data)):
            start =  datetime(*time.strptime(parse_data[index]["DTSTART"], "%Y%m%dT%H%M%SZ")[:6]).replace(tzinfo=utc).astimezone(tz)
            end =  datetime(*time.strptime(parse_data[index]["DTEND"], "%Y%m%dT%H%M%SZ")[:6]).replace(tzinfo=utc).astimezone(tz)

            if end < localtime:
                expired.append(index)
                continue

            parse_data[index]["DTSTART"] = start
            parse_data[index]["DTEND"] = end

        expired.reverse()
        for index in expired:
            parse_data.pop(index)

        parse_data.reverse()
        
        # 是否按照开始事件进行排序
        if sorted:
            parse_data.sort(key=lambda x :x['DTSTART'])
        
        self.parse_data = parse_data


    def get_localtime(self):
        """
        由于实验室主机时间配置问题，这里我们从网络获取时间。
        :return:
        """
        url = "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"
        response = requests.get(url)
        if response.status_code != 200:
            return None

        return json.loads(response.text)["data"]["t"][:10]


    def get_event(self, lens=10):
        """
        获取近期十场比赛
        :return:
        """
        return self.parse_data[:lens]
    
    
    def event_summary(self):
        events = self.get_event()

        tz = pytz.timezone("Asia/Shanghai")
        utc = pytz.timezone('UTC')

        timestamp = self.get_localtime()
        if timestamp is not None:
            localtime = datetime.fromtimestamp(int(timestamp)).astimezone(tz)
        else:
            localtime = datetime.now().astimezone(utc)

        notic = []
        for index, event in enumerate(events):
            running = "*" if event['DTSTART'] <= localtime <= event['SUMMARY'] else ""
            notic.append(f"{index+1}:{running}[{self.date4mat(event['DTSTART'])}] {event['SUMMARY']}")

        return  "近期十场比赛：\n" + \
                "\n".join(notic) + "\n" + \
                "---------------\n" + \
                "信息来源于CTFhub"


    def event_detail(self,index):
        event = self.get_event()[index]
        notic = []
        notic.append(f"[{event['SUMMARY']}]")
        notic.append(f"时间：{self.date4mat(event['DTSTART'])} ~ {self.date4mat(event['DTEND'])}")
        notic.append(f"地址：{event['URL']}")
        notic.append(f"赛制：{event['DESCRIPTION'][0]} {event['DESCRIPTION'][1]}")

        return "\n".join(notic)
        
    def date4mat(self, date:datetime):
        return date.strftime("%m-%d %H:%M")


if __name__=="__main__":
    vcalender = ctf_vcalendar()
    vcalender.query_event()
    vcalender.parse(sorted=True)
    print(vcalender.get_event())

