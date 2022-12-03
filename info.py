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


def ljust(input: str, len: int, pattern=" ") -> str:
    """
    对中文支持的ljust函数。由于中文输出后(例如在QQ中输出)实际所占空间是两个字母宽度。
    但是str的ljust函数并不会将中文的宽度识别为2，而是作为1，所以会出现对齐问题。
    :param input: 需要对齐的字符串
    :param len: 长度
    :param pattern: 填充使用的字符，默认为空格
    :return: 对齐的字符串
    """
    count = sum([2 if ord(x) > 127 else 1 for x in input])
    if count >= len: return input

    return input + pattern*(len - count)


if __name__=="__main__":
    print(ljust("aa", 4))
