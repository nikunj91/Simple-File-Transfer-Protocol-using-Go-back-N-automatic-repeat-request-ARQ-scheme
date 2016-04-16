#Simple-FTP sender

import sys
import collections

#Variables
ACK = 0 # ACK received from server.
sliding_window = set() #Ordered dictionary
client_buffer = collections.OrderedDict() #Ordered dictionary
N = 0

# Types of packets
TYPE_DATA = "0101010101010101"
TYPE_ACK = "1010101010101010"
TYPE_EOF = "1111111111111111"

def receive_ack():
	print "received"
	return 0
	
def send_packet(client_buffer(last_send_packet+1, host, port):
	print "packet sent"

def send_file(file_content, client_socket, host, port):
	last_send_packet = -1
	last_ack_packet = -1
	while len(client_buffer) != 0:
		while len(sliding_window) < N:
			send_packet(client_buffer(last_send_packet+1, host, port)
			last_send_packet = last_send_packet + 1
			sliding_window.add(last_send_packet)
		while 1:
			temp = receive_ack()
			for i in range(last_ack_packet+1,temp+1):
				sliding_window.remove(i)
				buffer.pop(i)
				last_ack_packet = temp
	
def main():
	global client_buffer 
	global N
	
	host = sys.argv[1]
    port = sys.argv[2]	
    file_name = sys.argv[3]
    N = sys.argv[4]	
    mss = sys.argv[5]
	
	port = int(port)
	N = int(N)
	mss = int(mss)
	
	#UDP datagram socket
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	max_window_size = N - 1
	
	sequence_number = 0
	try:
        with open(file_name, 'rb') as f:
            while True:
                chunk = f.read(int(MSS))  
                if chunk:
                    client_buffer[sequence_number] = chunk
                else:
                    break
        #print(file_content)
    except:
        sys.exit("Failed to open file!")
		
	send_file(client_buffer, client_socket, host, port)
	
	
if __name__ == "__main__":
    main()

