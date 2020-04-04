# import time
#
# import zmq
#
# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("tcp://*:5555")
# print('...starting up...')
#
# while True:
#     message = socket.recv_string()
#     print("Received request: %s" % message)
#
#     time.sleep(1)
#     socket.send_string("This is the servers reply!")



# import zmq
#
# context = zmq.Context()
#
# socket = context.socket(zmq.REP)
# socket.connect("tcp://127.0.0.1:5678")
#
# socket.send_string("Hello Jon")
# print(socket.recv_string())



# import socket
#
# MCAST_GRP = '224.1.1.1'
# MCAST_PORT = 5007
# # regarding socket.IP_MULTICAST_TTL
# # ---------------------------------
# # for all packets sent, after two hops on the network the packet will not
# # be re-sent/broadcast (see https://www.tldp.org/HOWTO/Multicast-HOWTO-6.html)
# MULTICAST_TTL = 2
#
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
# sock.sendto(b"robot", (MCAST_GRP, MCAST_PORT))



# import socket
# #
# # MCAST_GRP = '239.1.1.1'
# # MCAST_PORT = 1234
# #
# # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# # sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton("127.0.0.1"))
# # # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
# # print("Sending")
# # sock.sendto(bytearray("str()", "utf-8"), (MCAST_GRP, MCAST_PORT))
# #
# # data, address = sock.recvfrom(1024)
# # print('received %s bytes from %s' % (len(data), address))
# # print(data)



# import socket
#
# def connect(hostname, port):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     socket.setdefaulttimeout(1)
#     result = sock.connect_ex((hostname, port))
#     sock.close()
#     return result == 0
#
# for i in range(0,255):
#     ip_address = "192.168.1." + str(i)
#     res = connect(ip_address, 445)
#     if res:
#         print("Device found at: ", "192.168.1."+str(i) + ":"+str(22))
#     else:
#         print('IP Address: %s empty' % ip_address)


import socket
import struct
import sys

message = b'very important data'
multicast_group = ('224.3.29.71', 10000)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(0.2)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:

    # Send data to the multicast group
    print(sys.stderr, 'sending "%s"' % message)
    sent = sock.sendto(message, multicast_group)

    # Look for responses from all recipients
    while True:
        print(sys.stderr, 'waiting to receive')
        try:
            data, server = sock.recvfrom(16)
        except socket.timeout:
            print(sys.stderr, 'timed out, no more responses')
            break
        else:
            print(sys.stderr, 'received "%s" from %s' % (data, server))

finally:
    print(sys.stderr, 'closing socket')
    sock.close()