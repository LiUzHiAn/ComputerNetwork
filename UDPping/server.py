import random
from socket import *

# 创建一个UDP socket
# SOCK_DGRAM表示UDP协议  AF_INET表示IPV4
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", 6789))
# 注意，UDP协议不需要服务端监听  serverSocket.listen()
while True:
	# 随机丢包种子数
	rand = random.randint(0, 10)
	msg, addr = serverSocket.recvfrom(1024)
	# 将收到的msg转为大写
	msg = msg.upper()
	# 如果种子数小于4，就不回送数据(对ping程序的客户端来说相当于丢包)
	if rand < 4:
		continue
	serverSocket.sendto(msg, addr)

serverSocket.close()
