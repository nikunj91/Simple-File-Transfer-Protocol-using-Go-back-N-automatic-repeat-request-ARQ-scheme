#Simple-FTP sender

import sys
import collections
import pickle
import signal
import threading
from multiprocessing import Lock
from collections import namedtuple

#Variables
N = 0
RTT = 0.1
TYPE_DATA = "0101010101010101"
TYPE_ACK = "1010101010101010"
TYPE_EOF = "1111111111111111"
ACK_HOST = socket.gethostname()
ACK_PORT = 65000
max_seq_number=0
last_ack_packet = -1
last_send_packet = -1 # ACK received from server.
sliding_window = set() #Ordered dictionary
client_buffer = collections.OrderedDict() #Ordered dictionary
thread_lock = Lock()
data_packet = namedtuple('data_packet', 'sequence_no checksum type data')
ack_packet = namedtuple('ack_packet', 'sequence_no padding type')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sending_completed=False

SEND_HOST = sys.argv[1]
SEND_PORT = sys.argv[2]	
FILE_NAME = sys.argv[3]
N = sys.argv[4]	
MSS = sys.argv[5]

def retransmit_packet(packet, host, port, socket, sequence_no):
	global last_ack_packet
	if last_ack_packet<sequence_no:
		print "packet "+sequence_no+" timer expired"
		send_packet(packet, host, port, socket, sequence_no)


def send_packet(packet, host, port, socket, sequence_no):
	socket.sendto(packet, (host, port))
	t=threading.Timer(RTT,retransmit_packet,[packet,host,port,socket,sequence_no])
	t.start()
	print "packet "+sequence_no+" sent"

def rdt_send(file_content, client_socket, host, port):
	global last_send_packet,last_ack_packet,sliding_window,client_buffer
	while len(sliding_window)<min(len(client_buffer),N-1):
		if last_ack_packet==-1:
			send_packet(client_buffer[last_send_packet+1], host, port, client_socket, last_send_packet+1)
			last_send_packet = last_send_packet + 1
			sliding_window.add(last_send_packet)
	
def compute_checksum_for_chuck(chunk):
	checksum=0
	l=len(chunk)
	chunk=str(chunk)
	for byte in range(0,l,2):
		byte1=ord(chunk[byte])
		shifted_byte1=byte1<<8
		byte2=ord(chunk[byte+1])
		merged_bytes=shifted_byte1+byte2
		checksum_add=checksum+merged_bytes
		carryover=checksum_add>>16
		main_part=checksum_add&0xffff
		checksum=main_part+carryover
	checksum_complement=checksum^0xffff
	return checksum_complement

def ack_process:
	global last_ack_packet,last_send_packet,client_buffer,sliding_window,client_socket,SEND_PORT,SEND_HOST
	ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_socket.bind((ACK_HOST, ACK_PORT))
    while 1:
    	reply = pickle.loads(ack_socket.recv(65535))
    	if reply[2] == TYPE_ACK:
    		current_ack_seq_number=reply[0]-1
    		if last_ack_packet >= -1:
    			thread_lock.acquire()
    			if current_ack_seq_number == max_seq_number:
    				eof_packet = pickle.dumps(["0", "0", TYPE_EOF, "0"])
                    client_socket.sendto(eof_packet, (SERVER_HOST, SERVER_PORT))
                    thread_lock.release()
                    sending_completed=True
                    break
        		elif current_ack_seq_number>last_ack_packet:
        			while last_ack_packet<=current_ack_seq_number:
        				last_ack_packet=last_ack_packet+1
        				sliding_window.pop(last_ack_packet)
        				client_buffer.pop(last_ack_packet)
        				if last_send_packet<max_seq_number:
        					send_packet(client_buffer[last_send_packet+1],SEND_HOST,SEND_PORT,client_socket,last_send_packet+1)
        					last_send_packet=last_send_packet+1
        			thread_lock.release()




def main():
	global client_buffer ,max_seq_number,client_socket,N
	

	
	port = int(SEND_PORT)
	host = SEND_HOST
	N = int(N)
	mss = int(MSS)
	
	#UDP datagram socke
	
	max_window_size = N - 1
	
	sequence_number = 0
	try:
        with open(file_name, 'rb') as f:
            while True:
                chunk = f.read(int(MSS))  
                if chunk:
                	max_seq_number=sequence_number
                	chunk_checksum=compute_checksum_for_chuck(chunk)
                    client_buffer[sequence_number] = pickle.dumps([sequence_number,chunk_checksum,TYPE_DATA,chunk])
                    sequence_number=sequence_number+1
                else:
                    break
    except:
        sys.exit("Failed to open file!")

	ack_thread = threading.Thread(target=ack_process)
	ack_thread.start() 	
	rdt_send(client_buffer, client_socket, host, port)
	while 1:
		if sending_completed:
			break
	
if __name__ == "__main__":
    main()

