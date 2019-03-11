from socket import *

# 创建一个TCP套接字
tcpSerSock = socket(AF_INET, SOCK_STREAM)
# 绑定到9876端口
tcpSerSock.bind(("127.0.0.1", 9876))
# 最大连接数为5
tcpSerSock.listen(5)

while True:

	# Strat receiving data from the client
	print('Ready to serve...')
	tcpCliSock, addr = tcpSerSock.accept()
	print('Received a connection from:', addr)
	# 得到客户端发送的消息
	message = tcpCliSock.recv(2048).decode()

	# Extract the filename from the given message
	filename = message.split()[1].partition("//")[2].replace('/', '_')
	fileExist = "false"
	try:
		# 检查缓存中是否存在该文件
		f = open(filename, "r")
		outputdata = f.readlines()
		fileExist = "true"
		print('File Exists!')

		# ProxyServer finds a cache hit and generates a response message
		tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
		tcpCliSock.send("Content-Type:text/html\r\n".encode())

		# 如果缓存中存在，直接把数据发送给客户端
		for i in range(len(outputdata)):
			tcpSerSock.send(outputdata[i].encode())
		print('Read from cache')

	# 如果缓存中不存在客户端要请求的对象
	except IOError:
		if fileExist == "false":
			# Create a socket on the proxyserver
			# 在代理服务器上创建一个 tcp socket
			c = socket(AF_INET, SOCK_STREAM)

			try:
				# reference: https://github.com/moranzcw/Computer-Networking-A-Top-Down-Approach-NOTES
				# /blob/master/SocketProgrammingAssignment/
				hostn = message.split()[1].partition("//")[2].partition("/")[0]
				print('Host Name: ', hostn)
				# 连接到远程服务器的80端口 (http端口)
				c.connect((hostn, 80))
				print('Socket connected to port 80 of the host')

				# 代理服务器把客户端的请求送给目标服务器
				c.sendall(message.encode())

				rsps_buff = c.recv(2048)

				# Create a new file in the cache for the requested file.
				# Also send the response in the buffer to client socket and the corresponding file in the cache
				tmpFile = open("./" + filename, "w")
				tmpFile.writelines(rsps_buff.decode().replace('\r\n', '\n'))
				tmpFile.close()

				tcpCliSock.sendall(rsps_buff)
			except Exception as e:
				print(e)
				print("Illegal request")
		else:
			# HTTP response message for file not found
			print("HTTP response message for file not found!")

	# Close the client and the server sockets
	tcpCliSock.close()

tcpSerSock.close()


# http://gaia.cs.umass.edu/wireshark-labs/INTRO-wireshark-file1.html