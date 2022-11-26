# Summary

这是用于实验室的QQ机器人小项目。使用flask+gocqhttp的框架，搭建一个QQ机器人。

如果你有想要添加的功能，请自行fork开发，完成后提交合并请求。



# Usage

clone本库。然后安装必要python库。

```
pip install -r requirement.txt
```

随后使用pyhton运行main.py即可。



# Develop

基本的运行框架已经搭建完成。如果想要开发额外的功能，请新建文件开发。完成后在main.py添加对应的链接处理函数。



框架流程：

```
gocqhttp recive -> flask.route -> parse msg -> parse code -> run message function -> gocqhttp send
```



例如：我将要完成一个sqlite数据库接口。那么请创建对应的文件，其中写入代码逻辑。然后在main.py中写好你的处理函数，使用CommandParse的类调用装饰或者add_command函数将这个处理函数与对应的指令相连接即可。



关于CommandParse：

本类提供了一个保存指令和索引指令的类。其保存了一个指令树以及提示信息列表。

指令的格式为：

```
[target] [head] [code1] [code2] ... [-var value] [--stats] [param ...] 
```

target为cqhttp接入处理函数自动添加的，表示当前指令来源："group"群消息,"private"私人消息。

head为指令头，例如当前使用的/bot。随后跟随的时指令片。在"/bot show info"中，show和info都算作指令片。

如果一个指令片的开头是'-',"--"与' " '或者全是数字，那么这些指令片不会进入到指令树中。而是作为这条指令的参数传入到对应的函数中。

"--"开头表示bool类型变量，默认为False（需要你自己在函数的参数表中默认），如果存在则会将其置为True。

"-"开头表示变量，其后面一个指令片将作为此变量的值。

其他情况将作为元组参数。

例如：

```
group /bot show info --detail -grep "url" 12
```

那么程序接收到此指令是，将会进入到"group /bot show info"的处理函数中。其参数为：12, detail=True, grep="url"。

一旦解析遇到了参数类型，后面即使存在例如info， show等字段，都将会被解析为参数。指令的解析从遇到参数类型开始结束。

```
group /bot show --detail info -grep "url" 12
```

这条指令将会被解析为"group /bot show"的处理函数。而info会作为元组参数传入函数。请自行做好错误处理。



当我们需要将一个函数和一个指令链接时，可以使用add_command函数或者类调用

```python
# __call__(self, command, **options)
# add_command(self, command: list[str], link_func)

# parse = CommandParse()

@parse("group /bot; group /bot show")
def get_recent_event(*args, **kwargs):
    return ctfCaldendar.event_summary()

@parse("group /bot info", help="/bot info <i>, show the <i>st event detail")
def get_event_detail(*args, **kwargs):
    if len(args) < 1 or not args[0].isdigit(): return "参数错误"
    return ctfCaldendar.event_detail(int(args[0], 10))

parse.add_command("group /bot; group /bot show", get_recent_event)
```

链接函数参数请使用（*args， **kwargs）,随后自行对变量进行解包处理。由于传入的参数和用户输入有关，请做好错误处理。处理函数返回值要求为字符串或者无返回值。



关于info：

提供了一些控制台的模块化提示。

```python
from datetime import datetime

MSG_INFO = 0
MSG_WARN = 1
MSG_ERROR = 2

def info(msg, type=MSG_INFO):
    """
    输出信息
    :param msg: 需要输出的信息
    :param type: 信息的类型
    :return: 无返回
    """
    if type == MSG_INFO:  return f"\033[0;30m[{datetime.now().strftime('%F %H:%M:%S')}] [INFO]  {msg} \033[0m"
    if type == MSG_WARN:  return f"\033[0;33m[{datetime.now().strftime('%F %H:%M:%S')}] [WARN]  {msg} \033[0m"
    if type == MSG_ERROR: return f"\033[0;31m[{datetime.now().strftime('%F %H:%M:%S')}] [ERROR] {msg} \033[0m"

    raise TypeError("Unknown Message Type")
```

分为三种类型提示，颜色不同。注意默认是黑底白字（实验室服务器默认），如果你是白底黑字会看不见输出的。



功能实例：

```python
# file: sqlite.py
class sqlite:
	def __init__(self, target):
        ...
    def query(self, table, condition):
        ...
    def delete(self, table, condition):
        ...

# file:main.py 
from sqlite import sqlite
....

...
parse = CommandParse()

#如果你的对象需要长时间存在的话，请在此创建,这里我已经有一个长期实例ctfCaldendar。
ctfCaldendar = ctf_vcalendar()

# 添加你的处理函数, 使用装饰器方式
# 添加指令是带上参数不影响，解析时不会解析参数进入指令树
@parse("group /bot query -username 'alice' ", 
       help="/bot query -username username: query the user information by username")
def query_user(*args, **kwargs):
    if not "username" in kwargs.keys():
        return "no username provide"
    sql = sqlite()
    return sql.query(table = "flag", condition = kwargs["username"])

@parse("private /bot sql delete", 
       help="/bot sql delete -username username: delete the user information by username")
def delete(*args, **kwargs):
    ...
    
# 其他的功能模块
@parse("group /bot show")
def show(...):
    ...
    
...

# flask消息处理
@app.route("/event", methods = ["POST", "GET"])
def msg_event():
    ...

if __name__=="__main__":
    parse.add_command("group /bot query -username 'alice' ", query_user)
    parse.add_help("/bot query -username username: query the user information by username")
    ...
```

如果你的功能需要额外的python库，请在requirement.txt文件中添加。

如果你的功能需要额外的指令头，请在filter.json中添加正则匹配。





