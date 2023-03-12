import requests, time, random, urllib, json, traceback, re, websocket
from pbf import PBF
from statement.FaceStatement import FaceStatement
from statement.TextStatement import TextStatement
from statement import Statement
from statement.ImageStatement import ImageStatement
from utils.RegCmd import RegCmd

_name = "MC服务器"
_version = "1.0.1"
_description = "在QQ群内轻松管理MC服务器"
_author = "xzyStudio"
_cost = 0.00

class mcserver(PBF):
    def __enter__(self):
        return [
            RegCmd(
                name = "/",
                usage = "/<指令内容>",
                permission = "ao",
                function = "mcserver@command",
                description = "在服务器里执行指令",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "服务器状态",
                usage = "服务器状态",
                permission = "anyone",
                function = "mcserver@state",
                description = "服务器状态",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "启动服务器",
                usage = "启动服务器",
                permission = "ao",
                function = "mcserver@start",
                description = "开启服务器",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "关闭服务器",
                usage = "关闭服务器",
                permission = "ao",
                function = "mcserver@stop",
                description = "关闭服务器",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "面板数据",
                usage = "面板数据",
                permission = "ao",
                function = "mcserver@overview",
                description = "MCSM面板数据",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "获取状态 ",
                usage = "获取状态 <IP>:<端口>",
                permission = "anyone",
                function = "mcserver@getStatus",
                description = "获取指定服务器的状态",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "MC服务器消息同步",
                usage = "",
                permission = "anyone",
                function = "mcserver@syncMessage",
                description = "MC服务器消息同步",
                mode = "MC服务器",
                hidden = 1,
                type = "message"
            ),
            RegCmd(
                name = "加MC服务器指令",
                usage = "加MC服务器指令",
                permission = "ao",
                function = "mcserver@addMCCmd",
                description = "加MC服务器指令",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "MC服务器指令",
                usage = "MC服务器指令",
                permission = "ao",
                function = "mcserver@listMCCmd",
                description = "列出所有MC服务器指令",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "删MC服务器指令",
                usage = "删MC服务器指令 <群中指令名>",
                permission = "ao",
                function = "mcserver@delMCCmd",
                description = "删MC服务器指令",
                mode = "MC服务器",
                hidden = 0,
                type = "command"
            )
        ]
    
    def CheckAndGetSettings(self):
        setting = self.data.groupSettings
        if setting.get('MCSMApi') and setting.get('MCSMUuid') and setting.get('MCSMKey') and setting.get('MCSMRemote'):
            return setting
        else:
            return 404
    
    def CheckAndGetSettingsSocket(self):
        setting = self.data.groupSettings
        if len(setting.get("client_id").strip()) != 0 and len(setting.get("client_secret").strip()) != 0:
            return setting
        else:
            return 404
    
    def sendSocket(self, type, data, iff=True):
        setting = self.CheckAndGetSettingsSocket()
        if setting == 404:
            return False
        client_id = setting.get("client_id")
        client_secret = setting.get("client_secret")
        params = {
            "type": type,
            "data": data,
            "client_id": client_id,
            "client_secret": client_secret,
            "flag": "flag"
        }
        ws = websocket.WebSocket()
        ws.connect("wss://socket.xzynb.top/ws")
        ws.send(json.dumps(params))
        ws.close()
        if iff:
            self.client.msg().raw("face54 命令已发送！")
    
    def hum_convert(self, value):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size
    
    def state(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        setting = self.CheckAndGetSettings()
        if setting == 404:
            self.client.msg().raw('请先绑定服务器！\n绑定教程见作者B站：xzystudio1')
            return
        
        statusList = ["状态未知", "已停止", "正在停止", "正在启动", "正在运行"]
        
        dataa = requests.get(url='{0}/api/instance?uuid={1}&remote_uuid={2}&apikey={3}'.format(setting.get('MCSMApi'), setting.get('MCSMUuid'), setting.get('MCSMRemote'), setting.get('MCSMKey')))
        datajson = dataa.json()
        
        if datajson['status'] == 200:
            data = '[CQ:face,id=54] 实例ID：'+datajson['data']['instanceUuid']+'\n[CQ:face,id=54] 当前状态：'+statusList[datajson['data']['status']+1]+'\n[CQ:face,id=54] 服务器名称：'+str(datajson['data']['config']['nickname'])+'\n[CQ:face,id=54] 服务器类型：'+str(datajson['data']['config']['type'])+'\n[CQ:face,id=54] 在线人数：'+str(datajson['data']['info']['currentPlayers'])+'\n[CQ:face,id=54] 最大人数：'+str(datajson['data']['info']['maxPlayers'])
        else:
            data = '[CQ:face,id=151] 执行失败！\n原因：'+datajson.get('data')
        self.client.msg().raw(data)
    
    def stop(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        setting = self.CheckAndGetSettings()
        if setting == 404:
            setting = self.CheckAndGetSettingsSocket()
            if setting == 404:
                self.client.msg().raw('请先绑定服务器！\n绑定教程见作者B站：xzystudio1')
                return
            
            self.sendSocket("command", {"cmd":"stop"})
            return 
        
        dataa = requests.get(url='{0}/api/protected_instance/stop?uuid={1}&remote_uuid={2}&apikey={3}'.format(setting.get('MCSMApi'), setting.get('MCSMUuid'), setting.get('MCSMRemote'), setting.get('MCSMKey')))
        datajson = dataa.json()
        if datajson['status'] == 200:
            data = '[CQ:face,id=54] 执行成功！\n执行的实例：'+datajson['data']['instanceUuid']
        else:
            data = '[CQ:face,id=151] 执行失败！\n原因：'+datajson.get('data')
        self.client.msg().raw(data)
    
    def start(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        setting = self.CheckAndGetSettings()
        if setting == 404:
            self.client.msg().raw('请先绑定服务器！\n绑定教程见作者B站：xzystudio1')
            return
        
        dataa = requests.get(url='{0}/api/protected_instance/open?uuid={1}&remote_uuid={2}&apikey={3}'.format(setting.get('MCSMApi'), setting.get('MCSMUuid'), setting.get('MCSMRemote'), setting.get('MCSMKey')))
        datajson = dataa.json()
        
        if datajson['status'] == 200:
            data = '[CQ:face,id=54] 执行成功！\n执行的实例：'+datajson['data']['instanceUuid']
        else:
            data = '[CQ:face,id=151] 执行失败！\n原因：'+datajson.get('data')
        self.client.msg().raw(data)
    
    
    def overview(self):
        try:
            uid = self.data.se.get('user_id')
            gid = self.data.se.get('group_id')
            setting = self.CheckAndGetSettings()
            if setting == 404:
                self.client.msg().raw('请先绑定服务器！\n绑定教程见作者B站：xzystudio1')
                return
            
            dataa = requests.get(url='{0}/api/overview?apikey={1}'.format(setting.get('MCSMApi'), setting.get('MCSMKey')))
            datajson = dataa.json()
            if datajson.get('status') == 200:
                data = '[CQ:face,id=54] 面板状态：正常\n[CQ:face,id=54] 面板版本：'+datajson.get('data').get('version')+'\n[CQ:face,id=54] cpu使用率：'+str(datajson.get('data').get('process').get('cpu'))+'\n[CQ:face,id=54] 内存使用率：'+str(self.hum_convert(datajson.get('data').get('process').get('memory')))+'\n[CQ:face,id=54] 面板登陆次数：'+str(datajson.get('data').get('record').get('logined'))+'\n[CQ:face,id=54] 面板登陆失败次数：'+str(datajson.get('data').get('record').get('loginFailed'))+'\n[CQ:face,id=54] ban ip次数：'+str(datajson.get('data').get('record').get('banips'))+'\n[CQ:face,id=54] 当前系统时间：'+str(datajson.get('data').get('system').get('time'))+'\n[CQ:face,id=54] 系统总共内存：'+str(self.hum_convert(datajson.get('data').get('system').get('totalmem')))+'\n[CQ:face,id=54] 系统剩余内存：'+str(self.hum_convert(datajson.get('data').get('system').get('freemem')))+'\n[CQ:face,id=54] 系统类型：'+str(datajson.get('data').get('system').get('type'))+'\n[CQ:face,id=54] 主机名：'+str(datajson.get('data').get('system').get('hostname'))
            else:
                data = '[CQ:face,id=151] {0}'.format(datajson.get('data'))
            
            self.client.msg().raw(data)
        except Exception as e:
            self.client.msg().raw("[CQ:face,id=189] 获取数据出错，请检查MCSMApi是否正确")
        
    
    def command(self, iff=True):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message1 = self.data.message
        setting = self.CheckAndGetSettings()
        if setting == 404:
            setting = self.CheckAndGetSettingsSocket()
            if setting == 404:
                self.client.msg().raw('请先绑定服务器！\n绑定教程见作者B站：xzystudio1')
                return False
            
            self.sendSocket("command", {"cmd":self.data.message}, iff)
            return 
        
        #解码，需要指定原来是什么编码
        # message1 = message1.encode('gbk')
        #拿unicode进行编码
        # message1 = temp_unicode.encode('gbk')
        # self.CrashReport(message1, uuid=123456789)
    
        dataa = requests.get(url='{0}/api/protected_instance/command?uuid={1}&remote_uuid={2}&apikey={3}&command={4}'.format(setting.get('MCSMApi'), setting.get('MCSMUuid'), setting.get('MCSMRemote'), setting.get('MCSMKey'), message1))
        datajson = dataa.json()
        if datajson['status'] == 200:
            data = '[CQ:face,id=54] 执行成功！\n执行的实例：'+datajson['data']['instanceUuid']
        else:
            data = '[CQ:face,id=151] 执行失败！\n原因：'+datajson.get('data')
        if iff:
            self.client.msg().raw(data)
            dataa = requests.get(url='{0}/api/protected_instance/outputlog?uuid={1}&remote_uuid={2}&apikey={3}'.format(setting.get('MCSMApi'), setting.get('MCSMUuid'), setting.get('MCSMRemote'), setting.get('MCSMKey'))).json().get("data")
            data = dataa.split("\r\n")[-2]
            data = re.sub(r'\[0;([0-9]+);([0-9]+)m', "", data)
            data = re.sub(r'\[m', "", data)
            data = re.sub(r'>\[2K\r', "", data)
            data = re.sub(r'\[([0-9]+):([0-9]+):([0-9]+)\] \[Server thread/INFO\]: ', "", data)
            data = f"[CQ:reply,id={self.data.se.get('message_id')}] [CQ:face,id=54] 服务器返回：{data}"
            self.client.msg().raw(data)
    
    def MCSMAddUser(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        setting = self.CheckAndGetSettings()
        if setting == 404:
            self.client.msg().raw('请先绑定服务器！\n绑定教程见作者B站：xzystudio1')
            return
        
        dataa = requests.get(url='{0}/api/instance?uuid={1}&remote_uuid={2}&apikey={3}'.format(setting.get('MCSMApi'), setting.get('MCSMUuid'), setting.get('MCSMRemote'), setting.get('MCSMKey')))
        datajson = dataa.json()
        
    def getStatus(self):
        ip = self.data.message.split(':')
        port = 25565 if ':' not in self.data.message else ip[1]
        ip = ip[0]
        
        data = requests.get(f'https://mcapi.us/server/status?ip={ip}&port={port}').json()
        if data.get('status') == 'success':
            if len(data.get('players').get('sample')) < 10:
                players = ''
                for i in data.get('players').get('sample'):
                    players += f"\n    {i.get('name')}"
            else:
                players = '\n    玩家数量过多，无法显示全部'
            self.client.msg(
                Statement('reply', id=self.data.se.get('message_id')),
                ImageStatement(f'https://mcapi.us/server/image?ip={ip}&port={port}'),
                FaceStatement(54), TextStatement(self.data.message, 1),
                FaceStatement(54), TextStatement(f'MOTD：{data.get("motd")}', 1),
                FaceStatement(54), TextStatement(f'在线玩家数：{data.get("players").get("now")}/{data.get("players").get("max")}', 1),
                FaceStatement(54), TextStatement(f'在线玩家：{players}', 1),
                FaceStatement(54), TextStatement(f'服务器版本：{data.get("server").get("protocol")}')
            ).send()
        else:
            self.client.msg(
                Statement('reply', id=self.data.se.get('message_id')),
                FaceStatement(54), TextStatement('获取失败！')
            ).send()
        
    def syncMessage(self):
        # MC消息同步
        try:
            if self.data.groupSettings:
                if self.data.groupSettings.get('messageSync'):
                    message = self.data.message
                    self.data.message = 'say <'+str(self.data.se.get('sender').get('nickname'))+'> '+str(self.data.message)
                    if self.command(False) == False:
                        if random.randint(1, 5) == 3:
                            self.client.msg().raw("提示：关闭消息同步请发送： set messageSync===0")
                    else:
                        self.data.message = message
            
            commandList = self.mysql.selectx("SELECT * FROM `botMccmd` WHERE `qn`=%s", (self.data.se.get("group_id")))
            for i in commandList:
                name = i.get("name")
                cmd = i.get("cmd")
                if self.data.message[0:len(name)] == name:
                    # 执行指令
                    # cmd = re.sub(r'\$([0-9])+', "", cmd)
                    for l in cmd.split():
                        try:
                            num = l.find("$")
                            if num != -1:
                                num = int(l[num+1:num+2])
                            else:
                                continue
                            if num > len(self.data.args)-1:
                                self.client.msg().raw(f"参数不够，需要{num}个参数！")
                                return 
                            cmd = cmd.replace(f"${num}", self.data.args[num])
                        except Exception:
                            pass
                    
                    self.data.message = cmd
                    if self.command(False) == False:
                        self.client.msg().raw(f"[CQ:reply,id={self.data.se.get('message_id')}]执行失败")
                    else:
                        self.client.msg().raw(f"[CQ:reply,id={self.data.se.get('message_id')}]执行成功！")
        except Exception as e:
            pass
    
    def getuuid(self, name):
        mojangapi = 'https://api.mojang.com/users/profiles/minecraft/'+name
        page = urllib.request.urlopen(mojangapi)
        page = page.read()
        page = json.loads(page)
        dd = page['id']
        return dd.replace('"','')
    
    def hyp(self):
        try:
            api = HypixelAPI("14cf35d1-87a2-4f64-a69b-3a2ee85ac7a0")
            player_dict = api.get_player_json(self.getuuid(self.data.message))
            self.client.msg().raw(player_dict)
        except Exception as e:
            self.client.msg().raw(traceback.format_exc())
    
    def addMCCmd(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        ob = self.commandListener.get()
        if ob == 404:
            self.client.msg().raw('开始添加MC服务器指令，在此期间，你可以随时发送“退出”来退出加回复\n请发送在群中发送的指令')
            self.commandListener.set('mcserver@addMCCmd', {'name':''})
            return True
        
        step = int(ob.get('step'))
        args = ob.get('args')
        
        if step == 1:
            self.commandListener.set(args={'name':message})
            self.client.msg().raw('请发送在服务端执行的指令，使用“$数字”代替玩家输入的参数，请注意执行指令是在控制台执行，请自行斟酌指令前是否带“/”')
        
        if step == 2:
            self.commandListener.remove()
            
            self.mysql.commonx('INSERT INTO `botMccmd` (`name`, `cmd`, `qn`) VALUES (%s, %s, %s);', (args.get("name"), message, gid))
            self.client.msg().raw('添加成功！')
    
    def listMCCmd(self):
        arr = []
        commandList = self.mysql.selectx("SELECT * FROM `botMccmd` WHERE `qn`=%s", (self.data.se.get("group_id")))
        for i in commandList:
            arr.append({"type": "node", "data": {"name": self.data.botSettings.get("name"), "uin": self.data.botSettings.get("myselfqn"), "content": "{} => {}".format(i.get("name"), i.get("cmd"))}})
        self.client.CallApi("send_group_forward_msg", {"group_id":self.data.se.get("group_id"), "messages":arr})
    
    def delMCCmd(self):
        self.mysql.commonx("DELETE FROM `botMccmd` WHERE `qn`=%s AND `name`=%s", (self.data.se.get("group_id"), self.data.message))
        self.client.msg().raw("face54 删除成功！")