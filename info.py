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
