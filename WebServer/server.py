from socket import *

# AF_INET表示ipv4协议族，SOCK_STREAM指明用TCP
serverSocket = socket(AF_INET, SOCK_STREAM)

# 绑定到6789端口
serverSocket.bind(("", 6789))
# 最大连接数为5
serverSocket.listen(5)

while True:
	print("服务器准备就绪...")
	# TCP握手后建立连接套接字  如果是IP协议 addr是一个(hostaddr，port)的元组
	connectSocket, addr = serverSocket.accept()
	try:
		# 获取客户端发送的消息
		msg = connectSocket.recv(2048)
		print(msg)
		filename = msg.split()[1]
		f = open(filename[1:])
		outputdata = f.read()
		# 发送HTTP头到socket
		header = ' HTTP/1.1 200 OK\nConnection: close\nContent-Type: text/html\n' \
				 ' Content-Length: %d\n\n' % (len(outputdata))
		connectSocket.send(header.encode())

		# 发送数据
		for i in range(0, len(outputdata)):
			connectSocket.send(outputdata[i].encode())
		# 关闭连接
		connectSocket.close()

	except IOError:
		# 资源没找到
		fail_header = 'HTTP/1.1 404 Not Found'
		connectSocket.send(fail_header.encode())

		# 关闭连接
		connectSocket.close()

serverSocket.close()
