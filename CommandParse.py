class CommandParse:
    def __init__(self):
        self.Forset = {}
        self.code_help = []
        
        
    def __call__(self, command, **options) :
        def decorator(func):
            self.add_command(command, func)
            if "help" in options.keys(): self.add_help(options["help"])   
        return decorator
    
    # TODO: 增加对群或者私人的指令自动生成
    def add_command(self, command: list, link_func):
        """
        通过给定的指令，将指令添加到指令树中。树的每一层分别对应指令的不同部分。
        例如"/bot","!!" 可以分别为不同树的根节点，形成森林。
        如果command中的参数以-或者--开头将不会进入解析，而是作为参数传入对应的处理函数
        例如："/bot info -detail 1",detail将会不会单独作为一个节点,而是作为参数进入info函数的处理函数中。
        要求-code与--code与"str"与纯数字，全部作为参数。这些指令请自己进行处理。
        -code后面跟的值为code变量的值, --code表示状态。
        规定在出现参数之后，不能再出现指令，否则不会解析。例如：/bot -detail info 2 是不合法的，将会解析到/bot的处理函数中。
        不同的指令用 ';'区分

        Args:
            command (list): 输入的指令
            link_func (_type_): 需要绑定的函数
        Ret:
            None
        """
        if type(command) is str:
            command = command.split(';')
        elif type(command) is not list: # 类型错误
            return
        
        # 一棵树的表示为： {"/bot": {"info": {"func", link_func}, {"time":{"func":link_func}}}, {"show": {"func", link_func}}}
        # 叶子节点保存链接的函数，并且其键值为func
        # 上方的树其指令就有： 
        # /bot info 
        # /bot info time 
        # /bot show
        # 如果在info后面加上参数，也就是无法在子节点中索引到，或者后方没有下一个指令或者参数都将会索引func节点调用函数。
        for code in command:
            splited = code.split()
            ptr = self.Forset
            
            # parse and build command tree 
            for i in splited:
                
                if i.startswith("-") or i.startswith("--"): break
                if i.isdigit(): break
                if i.startswith('"') and i.endswith('"'): break
                
                if i not in ptr.keys():
                    ptr[i] = {}
                ptr = ptr[i]
            
            ptr["func"] = link_func
        
        
    # TODO: 添加对多条指令的解析
    def command_search(self, command: list):
        """
        返回对应指令的处理函数，与传入参数

        Args:
            command (list[str]): 需要查找的指令

        Returns:
            _type_: 处理函数， 函数参数元组
        """
        
        if type(command) is str:
            command = command.split()
        elif type(command) is not list: # 类型错误
            return
        
        ptr = self.Forset
        
        param = 0
        for index,i in enumerate(command):
            if i.startswith("-") or i.startswith("--"): break
            if i.isdigit(): break
            if i.startswith('"') and i.endswith('"'): break
            if i not in ptr.keys(): # 出现这个问题表示code写错了
                return "未知指令"
            ptr = ptr[i]
            param = index
        
        if "func" not in ptr.keys():    # 错误
            return "未知指令"
        
        param = command[param+1:]
        args, kwargs = self.parse_param(param)
    
        # 运行链接的函数
        return ptr["func"](*args, **kwargs)

    
    def parse_param(self,param:list):
        # 解析参数 格式为(*args, **kwargs)
        tuple_param = []
        key_param = {}
        
        for index, obj in enumerate(param):
            if not obj.startswith("-"): tuple_param.append(obj)
            if obj.startswith("--"):
                key_param[obj[2:]] = True
            if obj.startswith("-") and not obj.startswith("--"):
                
                # 首先判断后方是否有指令片
                if len(param)-1 < index + 1:
                    param.pop(index)    # 如果是结尾，后方没有指令片，不解析此变量
                    continue
                
                # 如果后方是--开头或者-var开头，不解析
                if param[index + 1].startswith("-"):
                    param.pop(index)
                    continue
                
                key_param[obj[1:]] = param[index + 1]
                param.pop(index + 1)
                
        return tuple_param, key_param
    
    # TODO: 添加帮助树，按照不同的头提供帮助信息
    def add_help(self,help:str):
        self.code_help.append(help)
        

    def help(self):
        return  "\n".join(self.code_help)



# test 部分
# a = CommandParse()
# def link_func1():
#     print("this is the link func1")        
    
# def link_func2():
#     print("this is the link func2")    

# def link_func3():
#     print("this is the link func3")    

# @a("/bot info", help="this is /bot info help")
# def link_func4(a, b, *args,**kwargs):
#     print("a =",a)
#     print("b =",b)
#     print("keys =", kwargs)
#     print("this is the link func4")     

# @a("/bot test; /bot aadd")
# def link_func5(*args,**kwargs):
#     print("this is link func5")

# if __name__=="__main__":
    # a.add_command("/bot show info 1", link_func1)
    # a.add_command("/bot show", link_func2)
    # a.add_command("/bot info -detail 12", link_func3)
    # a.add_command("!! ip show", link_func4)
    # a.add_command("/bot show detail 1", link_func4)
    # print(a.Forset)
    # a.command_search("/bot info")[0]()
    # a.command_search("/bot info 12")[0]()
    # a.command_search("/bot show detail 12")[0]()
    # a.command_search("/bot show")[0]()
    # print(a.command_search("/bot info"))
    # print(a.command_search("/bot info 12"))
    # print(a.command_search("/bot test"))
    # print(a.command_search("/bot aadd"))
    # a.command_search("/bot info --test 10 30 -var 12")
    # print(a.code_help)