import os, re, time
import itchat

def Execution(msg):
	command = msg['Text']
	print('command:', command)
	if re.search(r'(.*?)文件\[(.*?)\]', command):
		action, filename = re.search(r'(.*?)文件\[(.*?)\]',command).group(1, 2)
		return ViewDeleteFile(action, filename)
	elif re.search('^公众号签到$', command):
		return Signin()
	elif re.search(r'^查询好友状态$', command):
		return (3, '', '')
	elif re.match(r'^撤回附件列表$', command):
		return ReturnAttachmentList()
	else:
		itchat.send(r'支持查看删除文件、撤回附件列表', toUserName='filehelper')
		return (3, '指令', '失败')

def ViewDeleteFile(action, filename):
	if action == None or filename == None:
		itchat.send(r'亲，目前只支持两种指令：查看删除文件', toUserName='filehelper')
		return (3, '指令', '文件')

	if action == r'查看':
		if re.search(r'png|jpg|bmp|jepg|gif', filename):
			msg_type = 'Picture'
		elif re.search(r'avi|rm|mp4|mwv', filename):
			msg_type = 'Video'
		else:
			msg_type = 'fil'

		itchat.send('@%s@%s' %({'Picture' : 'img', 'Video' : 'vid'}.get(msg_type, 'fil'),
			r'.\\Revocation\\' + filename), toUserName='filehelper')
		return (2, action, filename)

	elif action == r'删除':
		if os.path.exists(r'.\\Revocation\\' + filename):
			os.remove(r'.\\Revocation\\')
			return(1, action, filename)

	return (0, action, filename)

def ReturnAttachmentList():
	filepath = '.\\Revocation\\'
	filelist = os.listdir(filepath)
	if filelist:
		msg_send(r'所有储存附件如下:')
		for item in filelist:
			msg_send += item + ' '
		itchat.send(msg_send, toUserName='filehelper')
	else:
		itchat.send(r'暂时没有撤回附件', toUserName='filehelper')
	return (3, '附件列表', '成功')
	



