from socket import *
import ssl

# some configurations
msg = "\r\n I love computer networks!"
endmsg = "\r\n.\r\n"  # SMTP中定义的邮件结尾
mail_from = "********@***.com"
mail_to = "********@***.com"
username = "**********"  # base64 密文
password = "**********"  # base64 密文
hostname = "smtp.163.com"
mailserver = ("smtp.163.com", 25)  # 邮件服务器

# 与邮件服务器建立TCP连接 （SSL）
clientSocket = socket(AF_INET, SOCK_STREAM)
# clientSocket = ssl.wrap_socket(clientSocket, ssl_version=ssl.PROTOCOL_SSLv23)
clientSocket.connect(mailserver)

# 邮件服务器响应
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
	print("220 reply not received from server!")

# 向邮件服务器发送HELO 命令
HELO_cmd = "HELO Andy\r\n"
clientSocket.send(HELO_cmd.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != "250":
	print("250 reply not received from server!")

# 向邮件服务器发送 AUTH LOGIN 命令
clientSocket.sendall("AUTH LOGIN\r\n".encode())
AUTH_LOGIN_recv = clientSocket.recv(1024).decode()
print(AUTH_LOGIN_recv)
if AUTH_LOGIN_recv[:3] != "334":
	print("334 reply not received from server!")

# 向邮件服务器发送用户名
clientSocket.sendall((username + '\r\n').encode())
username_recv = clientSocket.recv(1024).decode()
print(username_recv)
if (username_recv[:3] != '334'):
	print('334 reply not received from server')

# 向邮件服务器发送密码
clientSocket.sendall((password + '\r\n').encode())
password_recv = clientSocket.recv(1024).decode()
print(password_recv)
if (password_recv[:3] != '235'):
	print('235 reply not received from server')

# 向邮件服务器发送 MAIL FROM 命令
MAIL_FROM_cmd = "MAIL FROM <" + mail_from + ">\r\n"
clientSocket.send(MAIL_FROM_cmd.encode())
MAIL_FROM_recv = clientSocket.recv(1024).decode()
print(MAIL_FROM_recv)
if MAIL_FROM_recv[:3] != "250":
	print("250 reply not received from server!")

# 向邮件服务器发送 RECP TO 命令
RECP_TO_cmd = "RECP TO <" + mail_from + ">\r\n"
clientSocket.send(RECP_TO_cmd.encode())
RECP_TO_recv = clientSocket.recv(1024).decode()
print(RECP_TO_recv)
if RECP_TO_recv[:3] != "250":
	print("250 reply not received from server!")

# 向邮件服务器发送 DATA 命令
DATA_cmd = "DATA\r\n"
clientSocket.send(DATA_cmd.encode())
DATA_recv = clientSocket.recv(1024).decode()
print(DATA_recv)
if DATA_recv[:3] != "354":
	print("354 reply not received from server!")

# 邮件内容
# Send message data.
message = 'from:' + mail_from + '\r\n'
message += 'to:' + mail_to + '\r\n'
message += 'subject:' + msg + '\r\n'
message += 'Content-Type:text/plain\t\n'
message += '\r\n' + msg
clientSocket.sendall(message.encode())

# 邮件以.结尾
clientSocket.sendall(endmsg.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if (recv[:3] != '250'):
	print('250 reply not received from server')

# 客户端先quit
clientSocket.sendall('QUIT\r\n'.encode())

# 关闭socket连接
clientSocket.close()
