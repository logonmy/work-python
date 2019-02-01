# Echo client program
import socket
import sys

HOST = '127.0.0.1'    # The remote host
PORT = 21567              # The same port as used by the server
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print 'could not open socket'
    sys.exit(1)
writer = s.makefile('w')
send_data = bytearray(b'\xee\xee\xff\xff\xf5\x00\x00\x00\x00\x00\x00\x00query_type:TQUERY\nquery_address:\xc9\xee\xdb\xda\xca\xd0\xc4\xcf\xc9\xbd\xc7\xf8\xbf\xc6\xbc\xbc\xd6\xd0\xd2\xbb\xc2\xb7\xbb\xaa\xc7\xbf\xb8\xdf\xd0\xc2\xb7\xa2\xd5\xb9\xb4\xf3\xc2\xa512\xc2\xa51201-1206\nquery_tel:0755-66826666\ndata_type:poi\nkeywords:\xbb\xaa\xc7\xbf\xb7\xbd\xcc\xd8\xc9\xe8\xbc\xc6\xd4\xba\xa3\xa8\xc9\xee\xdb\xda\xa3\xa9\xd3\xd0\xcf\xde\xb9\xab\xcb\xbe\ncity:440300\npage_num:10\npage:1\neid:\ntemplateid:\nuserid:\nsort_rule:7\nshow_score:true')
writer.write(send_data)
data = s.recv(1024)
print 'Received', repr(data)
# s.sendall(send_data)
# data = s.recv(1024)
# print 'Received', repr(data)
# s.sendall(send_data)
# data = s.recv(1024)
# print 'Received', repr(data)
# s.close()
# print 'Received', repr(data)