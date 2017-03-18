# -*-encoding:utf-8-*-
import os
import re
import shutil
import time

import itchat
from itchat.content import *

import Execution

# {msg_id:(msg_from,msg_to,msg_time,msg_time_touser,msg_type,msg_content,msg_url)}
msg_store = {}


# ClearTimeOutMsg用于清理消息字典，把超时消息清理掉
# 为减少资源占用，此函数只在有新消息动态时调用
def ClearTimeOutMsg():
    if msg_store.__len__() > 0:
        for msgid in list(msg_store):  # 由于字典在遍历过程中不能删除元素，故使用此方法
            #print("TimeOut:", time.time() - msg_store.get(msgid, None)["msg_time"])
            if time.time() - msg_store.get(msgid, None)["msg_time"] > 130.0:  # 超时两分钟
                item = msg_store.pop(msgid)

                # 可下载类消息，并删除相关文件
                if item['msg_type'] == "Picture" \
                        or item['msg_type'] == "Recording" \
                        or item['msg_type'] == "Video" \
                        or item['msg_type'] == "Attachment":
                    print("要删除的文件：", item['msg_content'])
                    os.remove(".\\Cache\\" + item['msg_content'])


# 将接收到的消息存放在字典中，当接收到新消息时对字典中超时的消息进行清理
# 没有注册note（通知类）消息，通知类消息一般为：红包 转账 消息撤回提醒等，不具有撤回功能
@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS], 
                    isFriendChat=True,  isGroupChat=True)
def Revocation(msg):
    # 处理指令
    itchat.get_friends(update=True)
    #print("Test",msg)
    if msg['ToUserName'] == "filehelper" and msg['Type'] == "Text":
        result = Execution.Execution(msg)

        if result[0] == 0:
            itchat.send(result[1] + r"文件:" + result[2] + r" 失败", toUserName="filehelper")
        elif result[0] == 1:
            itchat.send(r"删除文件:" + result[2] + r" 成功", toUserName="filehelper")
        else:
            pass
        return

    mytime = time.localtime()  # 这儿获取的是本地时间
    # 获取用于展示给用户看的时间 2017/03/03 13:23:53
    msg_time_touser = mytime.tm_year.__str__() \
                      + "/" + mytime.tm_mon.__str__() \
                      + "/" + mytime.tm_mday.__str__() \
                      + " " + mytime.tm_hour.__str__() \
                      + ":" + mytime.tm_min.__str__() \
                      + ":" + mytime.tm_sec.__str__()

    msg_id = msg['MsgId']  # 消息ID
    msg_time = msg['CreateTime']  # 消息时间
    if itchat.search_friends(userName=msg['FromUserName']):
        if itchat.search_friends(userName=msg['FromUserName'])['RemarkName']:
            msg_from = itchat.search_friends(userName=msg['FromUserName'])['RemarkName']  # 消息发送人备注
        elif itchat.search_friends(userName=msg['FromUserName'])['NickName']:  # 消息发送人昵称
            msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']  # 消息发送人昵称
        else:
            msg_from = r"读取发送消息好友失败"
    else:
        msg_from = msg['ActualNickName']
    msg_type = msg['Type']  # 消息类型
    msg_content = None  # 根据消息类型不同，消息内容不同
    msg_url = None  # 分享类消息有url
    # 图片 语音 附件 视频，可下载消息将内容下载暂存到当前目录
    if msg['Type'] == 'Text':
        msg_content = msg['Text']
    elif msg['Type'] == 'Picture':
        msg_content = msg['FileName']
        msg['Text'](msg['FileName'])
        shutil.move(msg_content, r".\\Cache\\")
    elif msg['Type'] == 'Card':
        msg_content = msg['RecommendInfo']['NickName'] + r" 的名片"
    elif msg['Type'] == 'Map':
        
        x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
        if location is None:                                                                                                           
            msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()
        else:
            msg_content = r"" + location
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_url = msg['Url']
    elif msg['Type'] == 'Recording':
        msg_content = msg['FileName']
        msg['Text'](msg['FileName'])
        shutil.move(msg_content, r".\\Cache\\")
    elif msg['Type'] == 'Attachment':
        msg_content = msg['FileName']
        msg['Text'](msg['FileName'])
        shutil.move(msg_content, r".\\Cache\\")
    elif msg['Type'] == 'Video':
        msg_content = msg['FileName']
        msg['Text'](msg['FileName'])
        shutil.move(msg_content, r".\\Cache\\")
    elif msg['Type'] == 'Friends':
        msg_content = msg['Text']

        # print(r"消息提取",
        # {"msg_from": msg_from, "msg_time": msg_time, "msg_time_touser": msg_time_touser, "msg_type": msg_type,
        # "msg_content": msg_content, "msg_url": msg_url})
    print("消息提取", msg)
    # 更新字典
    # {msg_id:(msg_from,msg_time,msg_time_touser,msg_type,msg_content,msg_url)}
    msg_store.update(
        {msg_id: {"msg_from": msg_from, "msg_time": msg_time, "msg_time_touser": msg_time_touser,
                "msg_type": msg_type, "msg_content": msg_content, "msg_url": msg_url}})
    # 清理字典
    ClearTimeOutMsg()


@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True)
def SaveMsg(msg):
    # print(msg)
    # 创建可下载消息内容的存放文件夹，并将暂存在当前目录的文件移动到该文件中
    if not os.path.exists(".\\Revocation\\"):
        os.mkdir(".\\Revocation\\")

    itchat.search_chatrooms()
    if re.search(r"\!\[CDATA\[.*撤回了一条消息\]\]", msg['Content']) != None:
        print("撤回Msg", msg)
        if re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']) != None:
            old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        elif re.search("\;msgid\&gt\;(.*?)\&lt", msg['Content']) != None:
            old_msg_id = re.search("\;msgid\&gt\;(.*?)\&lt", msg['Content']).group(1)
        old_msg = msg_store.get(old_msg_id, {})

        print(r"撤回的消息", old_msg_id, old_msg)
        if old_msg:
            msg_send = r"您的好友：" \
                       + old_msg.get('msg_from', None) \
                       + r"  在 [" + old_msg.get('msg_time_touser', None) \
                       + r"], 撤回了一条 [" + old_msg.get('msg_type', None) + "] 消息, 内容如下:" \
                       + old_msg.get('msg_content', None)
            if old_msg['msg_type'] == "Sharing":
                msg_send += r", 链接: " + old_msg.get('msg_url', None)
            elif old_msg['msg_type'] in ['Picture', 'Recording', 'Video', 'Attachment']:
                msg_send += r", 存储在当前目录下Revocation文件夹中"
                shutil.move(r".\\Cache\\" + old_msg['msg_content'], r".\\Revocation\\")
        else:
            msg_send = r"您的好友可能撤回了一个微信表情包，暂时不支持微信表情包，请谅解。"

        itchat.send(msg_send, toUserName='filehelper')  # 将撤回消息的通知以及细节发送到文件助手

        msg_store.pop(old_msg_id)


if __name__ == '__main__':
    ClearTimeOutMsg()
    if not os.path.exists(".\\Cache\\"):
        os.mkdir(".\\Cache\\")
    itchat.auto_login(hotReload=True)
    itchat.run()