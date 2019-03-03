from socket import *
import time

hostName = "127.0.0.1"
servrPort = 6789
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)

for i in range(10):
	try:
		sendTime = time.time()
		# 生成数据报，编码为bytes以便发送
		msg = ("Ping %d %s" % (i + 1, sendTime)).encode()
		clientSocket.sendto(msg,(hostName,servrPort))
		# 从服务端得到的消息
		msg_recieved, server_addr = clientSocket.recvfrom(1024)
		# 计算往返时间
		rtt = time.time() - sendTime
		# 显示信息
		print('从%s得到的第%d个数据包,往返延时:%.3f(s)' % (hostName, i + 1, rtt))
	except IOError as e:
		print('第%d个数据包丢失' % (i + 1))

# 关闭套接字
clientSocket.close()
