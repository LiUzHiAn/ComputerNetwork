from socket import *
import time

hostName = "127.0.0.1"
servrPort = 6789
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(2)  # 设置最大等待时间为2s

packet_sent = 8
packet_received = 0

# ms为单位
max_rrt = -1
min_rrt = 10  # 初始化时大于timeout时间即可
avg_rrt = 0
print("Pinging %s with %d packets:" % (hostName, packet_sent))
for i in range(packet_sent):
	try:
		sendTime = time.time()
		# 生成数据报，编码为bytes以便发送
		msg = ("packet %d" % (i + 1)).encode()

		clientSocket.sendto(msg, (hostName, servrPort))
		# 从服务端得到的消息
		msg_recieved, server_addr = clientSocket.recvfrom(1024)
		# 计算往返时间
		rtt = (time.time() - sendTime) * 1000
		if rtt > max_rrt:
			max_rrt = rtt
		if rtt < min_rrt:
			min_rrt = rtt
		avg_rrt += rtt
		# 显示信息
		print('Packet %d, Reply from: %s, RTT:%.2f(ms)' % (i + 1, hostName, rtt))
		packet_received += 1
	except IOError as e:
		print('Packet %d, Reply from: %s, Lost' % (i + 1, hostName))
		max_rrt = 1
		avg_rrt += 1

# 丢包率统计
avg_rrt /= packet_sent
packet_lost = packet_sent - packet_received
print("Ping statistics for %s:" % hostName)
print("\tPackets: Sent = %d, Received = %d, Lost = %d (%.1f%% loss)"
	  % (packet_sent, packet_received, packet_lost, packet_lost / packet_sent * 100))
print("Approximate round trip times in milli-seconds:")
print("\tMinimum = %dms, Maximum = %dms, Average = %dms" % (min_rrt, max_rrt, avg_rrt))

# 关闭套接字
clientSocket.close()
