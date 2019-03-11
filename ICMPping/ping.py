import socket
import os
import sys
import struct
import time
import select

# ICMP报文中请求回显类型号
ICMP_ECHO_REQUEST = 8


def checksum(str):
	csum = 0  # 校验和  （一个32位十进制数，因为每16位相加时可能会产生进位（即溢出），这些溢出将会被回卷）
	# 奇偶控制，如果总长的字节数为奇数时，肯定最后一个字节要单独相加（求校验和时是每16位一加）
	countTo = (len(str) // 2) * 2
	count = 0
	while count < countTo:
		# ord()函数返回一个字符的ASCII码
		# 取两个字节，第二个字节放在16位的高位，第一个字节放在16位的地位
		thisVal = (str[count + 1] << 8) + str[count]
		csum = csum + thisVal
		# 这里和0xffffffff进行and运算主要是为了保留每次运算过程中可能出现的16位溢出，
		# 这样一来，就可以将溢出位（也就是进位）保存到sum的高16位
		csum = csum & 0xffffffff
		count = count + 2  # 后移两个字节，也就是准备求和下一个16位

	# 如果真的有一个字节剩余
	if countTo < len(str):
		csum = csum + str[len(str) - 1].decode()
		csum = csum & 0xffffffff

	# 把csum的高16位溢出回卷，加到低16位上
	csum = (csum >> 16) + (csum & 0xffff)
	# 如果还产生了溢出，再操作一次
	csum = csum + (csum >> 16)
	# 求反码
	answer = ~csum
	answer = answer & 0xffff
	# 这里进行字节序大小端转换，因为网络字节序是大端模式
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer


def receiveOnePing(mySocket, ID, sequence, destAddr, timeout):
	timeLeft = timeout

	while 1:
		startedSelect = time.time()
		whatReady = select.select([mySocket], [], [], timeLeft)
		howLongInSelect = (time.time() - startedSelect)
		if whatReady[0] == []:  # Timeout
			return None

		timeReceived = time.time()
		recPacket, addr = mySocket.recvfrom(1024)

		# Fill in start
		header = recPacket[20: 28]
		type, code, checksum, packetID, sequence = struct.unpack("!bbHHh", header)
		if type == 0 and packetID == ID:  # type should be 0
			byte_in_double = struct.calcsize("!d")
			timeSent = struct.unpack("!d", recPacket[28: 28 + byte_in_double])[0]
			delay = timeReceived - timeSent
			ttl = ord(struct.unpack("!c", recPacket[8:9])[0].decode())
			return (delay, ttl, byte_in_double)
		# Fill in end

		timeLeft = timeLeft - howLongInSelect
		if timeLeft <= 0:
			return None


def sendOnePing(mySocket, ID, sequence, destAddr):
	# Header is type (8), code (8), checksum (16), id (16), sequence (16)

	myChecksum = 0
	# Make a dummy header with a 0 checksum.
	# struct -- Interpret strings as packed binary data
	header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
	data = struct.pack("!d", time.time())
	# Calculate the checksum on the data and the dummy header.
	myChecksum = checksum(header + data)

	header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
	packet = header + data

	mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


# Both LISTS and TUPLES consist of a number of objects
# which can be referenced by their position number within the object


def doOnePing(destAddr, ID, sequence, timeout):
	icmp = socket.getprotobyname("icmp")

	# SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw

	# Fill in start
	mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	# Fill in end

	sendOnePing(mySocket, ID, sequence, destAddr)
	delay = receiveOnePing(mySocket, ID, sequence, destAddr, timeout)

	mySocket.close()
	return delay


def ping(host, timeout=1):
	# timeout=1 means: If one second goes by without a reply from the server,
	# the client assumes that either the client’s ping or the server’s pong is lost
	dest = socket.gethostbyname(host)
	print("Pinging " + dest + " using Python:")
	print("")
	# Send ping requests to a server separated by approximately one second

	myID = os.getpid() & 0xFFFF  # Return the current process i
	loss = 0
	for i in range(4):
		result = doOnePing(dest, myID, i, timeout)
		if not result:
			print("Request timed out.")
			loss += 1
		else:
			delay = int(result[0] * 1000)
			ttl = result[1]
			bytes = result[2]
			print("Received from " + dest + ": byte(s)=" + str(bytes) + " delay=" + str(delay) + "ms TTL=" + str(ttl))
		time.sleep(1)  # one second
	print("Packet: sent = " + str(4) + " received = " + str(4 - loss) + " lost = " + str(loss))

	return


if __name__ == '__main__':
	if len(sys.argv) <= 1:
		print("Usage : ping [host ip or hostname]")
		sys.exit(2)
	ping(sys.argv[1])
