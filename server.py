#Receiver side of the Go-back-N protocol
import socket
import pickle
import random
import sys

SERVER_PORT = 7735
FILE_NAME = sys.argv[2]
PACKET_LOSS_PROB = float(sys.argv[3])
TYPE_DATA = "0101010101010101"
TYPE_ACK = "1010101010101010"
TYPE_EOF = "1111111111111111"
DATA_PAD = "0000000000000000"
ACK_PORT = 65000
HOST_NAME = socket.gethostname()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST_NAME, SERVER_PORT))
last_received_packet=-1

def compute_checksum_for_chuck(chunk,checksum):
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

def is_checksum_proper(chunk,checksum):
	return compute_checksum_for_chuck(chunk,checksum)==0

def check_if_packet_drop(PACKET_LOSS_PROB,packet_sequence_number):
	return random.random()<PACKET_LOSS_PROB

def send_acknowledgement(ack_number):
	print "ack "+str(ack_number)+" sent"
	ack_packet = pickle.dumps([acknowledgement, DATA_PAD, TYPE_ACK])
	ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ack_socket.sendto(ack_packet,(HOST_NAME, ACK_PORT))
	ack_socket.close()

def write_data_to_file(packet_data):
	with open(FILE_NAME, 'ab') as file:
		file.write(packet_data)

def main():
	global last_received_packet
	completed=False
	#print 'inside main'
	while not completed:
		print 'while'
		received_data1, addr = server_socket.recvfrom(65535)
		print 'got'
		print received_data1
        received_data = pickle.loads(received_data1)
        print 'DATA RECEIVED'
        packet_sequence_number, packet_checksum, packet_type, packet_data = received_data[0], received_data[1], received_data[2], received_data[3]
        if packet_type == TYPE_EOF:
        	print("File Received from client..Yaaaaaaaay")
        	completed=True
        	server_socket.close()
        elif packet_type == TYPE_DATA:
        	print("Packet "+ str(packet_sequence_number)+ " received")
        	drop_packet=check_if_packet_drop(PACKET_LOSS_PROB,packet_sequence_number)
        	if drop_packet==True:
        		print "Packet "+packet_sequence_number+" has been dropped due to less probability"
        	else:
				if is_checksum_proper(packet_data,packet_checksum):
					if packet_sequence_number==last_received_packet+1:
						send_acknowledgement(packet_sequence_number+1)
						last_received_packet=last_received_packet+1
						write_data_to_file(packet_data)
					else:
						send_acknowledgement(last_received_packet+1)
				else:
					print "Packet "+packet_sequence_number+" has been dropped due to improper checksum"

if __name__ == "__main__":
    main()

