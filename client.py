#!/usr/bin/python           
#This is the client code
#Author Nikunj Shah
#Author Aparna Patil

import socket
import sys
import collections
import pickle
import signal
import threading
from multiprocessing import Lock
from collections import namedtuple
import time

#Constant Declarations

RTT = 0.1 # Assumed value for timeouts

#Defining the types of packets
TYPE_DATA = "0101010101010101"
TYPE_ACK = "1010101010101010"
TYPE_EOF = "1111111111111111"
ACK_HOST = '0.0.0.0'
print ACK_HOST
ACK_PORT = 65000 

#Variable Declaration
max_seq_number=0 #sequence number of the last packet
last_ack_packet = -1  # ACK received from server.
last_send_packet = -1  # Last packet sequence number sent to the server
sliding_window = set() # Maintain the Slding window at the sender end
client_buffer = collections.OrderedDict() # Will act as a buffer and keep all the packets that are yet to be sent to the receiver

#Defining the namedtuples that will work as a complete packet including header and data that will be used for packet exchanges 
data_packet = namedtuple('data_packet', 'sequence_no checksum type data')
ack_packet = namedtuple('ack_packet', 'sequence_no padding type')

#Initially thread lock will be acquired here
thread_lock = Lock()

#Client end socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Will keep a track whether sending has completed or not
sending_completed=False

#Maintain the time to be used for report generation
t_start=0
t_end=0

#Values taken from the command line
#Host of the server
SEND_HOST = sys.argv[1]
#Server Port
SEND_PORT = int(sys.argv[2])
#File Name
FILE_NAME = sys.argv[3]
#Window Size
N = int(sys.argv[4])
#MSS Size
MSS = int(sys.argv[5])

#Send the packet to the host details in the parameters
def send_packet(packet, host, port, socket, sequence_no):
	client_socket.sendto(packet,(SEND_HOST,SEND_PORT)) #(SEND_HOST, SEND_PORT))

#Will handle the initial packet sending till the receipt of the acknowledgement from the receiver or sliding window is full
def rdt_send(file_content, client_socket, host, port):
	global last_send_packet,last_ack_packet,sliding_window,client_buffer,t_start
	#Timer starts as first packet is send from here
	t_start=time.time()
	#Send packets till the sliding window is full or all packets are sent
	while len(sliding_window)<min(len(client_buffer),N):
		#Till the time no acknowledgement arrives from receiver
		if last_ack_packet==-1:
			#Send the packet
			send_packet(client_buffer[last_send_packet+1], host, port, client_socket, last_send_packet+1)
			#Set the timer for retransmission
			signal.alarm(0)
 			signal.setitimer(signal.ITIMER_REAL, RTT)
 			#Increment the packet sequence number
			last_send_packet = last_send_packet + 1
			#Add the packet to the sliding window
			sliding_window.add(last_send_packet)
			y=0
			while y<100000:
				y=y+1

#Will compute the checksum for the chunk of data provided
def compute_checksum_for_chuck(chunk):
	checksum=0
	l=len(chunk)
	chunk=str(chunk)
	byte=0
	while byte<l:
		#Take 2 bytes of from the chunk data...takes 0xffff if the byte2 is not there because of odd chunk size
		byte1=ord(chunk[byte])
		shifted_byte1=byte1<<8
		if byte+1==l:
			byte2=0xffff
		else:
			byte2=ord(chunk[byte+1])
		#Merge the bytes in the form of byte1byte2 to make 16bits
		merged_bytes=shifted_byte1+byte2
		#Add to the 16 bit chekcsum computed till now
		checksum_add=checksum+merged_bytes
		#Compute the carryover
		carryover=checksum_add>>16
		#Compute the main part of the new checksum
		main_part=checksum_add&0xffff
		#Add the carryover to the main checksum again
		checksum=main_part+carryover
		#Do same for next 2 bytes
		byte=byte+2
	#Take 1's complement of the computed checksum and return it
	checksum_complement=checksum^0xffff
	return checksum_complement

#will monitor the incoming ack's and sent the remaining packets
def ack_process():
	global last_ack_packet,last_send_packet,client_buffer,sliding_window,client_socket,SEND_PORT,SEND_HOST,sending_completed,t_end,t_start,t_total
	#Create the server socket that will listen for incoming ack's
	ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ack_socket.bind((ACK_HOST, ACK_PORT))

	while 1:
		#Receive the ACK
		reply = pickle.loads(ack_socket.recv(65535))
		#If it incoming packet is an ACK
		if reply[2] == TYPE_ACK:
			#Retrieve the sequence number in the ACK to get the last ACK'ed packet
			current_ack_seq_number=reply[0]-1
			if last_ack_packet >= -1:
				#Acquire the thread control
				thread_lock.acquire()
				#If this is the last ACK, send the EOF Packet to receiver
				#Release the thread control
				#Maintain the end time
    			if current_ack_seq_number == max_seq_number:
    				#Create the EOF Packet and send it
    				eof_packet = pickle.dumps(["0", "0", TYPE_EOF, "0"])
    				client_socket.sendto(eof_packet, (SEND_HOST, SEND_PORT))
    				#Release the thread
    				thread_lock.release()
    				#Mark sending as complete
    				sending_completed=True
    				#Record the end time of the transfer
    				t_end=time.time()
    				t_total=t_end-t_start
    				break
    			#Else if not the last ACK and also not ACK of a packet already ACK'ed by a higher sequence number ACK
    			elif current_ack_seq_number>last_ack_packet:
    				# if new ACK recieved
        			while last_ack_packet<current_ack_seq_number:
        				#Reset the timer again
        				signal.alarm(0)
        				signal.setitimer(signal.ITIMER_REAL, RTT)
        				#Reset the value of last receiveed ack
        				last_ack_packet=last_ack_packet+1
        				#Remvove the ACK'ed packet from the sliding window and the buffer
        				sliding_window.remove(last_ack_packet)
        				client_buffer.pop(last_ack_packet)
        				#Send the packets till the sliding window has space
        				while len(sliding_window)<min(len(client_buffer),N):
	        				if last_send_packet<max_seq_number:
	        					send_packet(client_buffer[last_send_packet+1],SEND_HOST,SEND_PORT,client_socket,last_send_packet+1)
	        					sliding_window.add(last_send_packet+1)
	        					last_send_packet=last_send_packet+1
	        		#Release the thread lock
        			thread_lock.release()
        		else:
        			thread_lock.release()

#Handle the timeouts
def timeout_thread(timeout_th, frame):
	global last_ack_packet
 	if last_ack_packet==last_send_packet-len(sliding_window):
 		print "Timeout, sequence number = "+str(last_ack_packet+1)
 		#Acquire the thread lock
 		thread_lock.acquire()
 		#Resend all the packets in the sliding window from the timeout packet
 		for i in range(last_ack_packet+1,last_ack_packet+1+len(sliding_window),1):
 			signal.alarm(0)
 			signal.setitimer(signal.ITIMER_REAL, RTT)
			send_packet(client_buffer[i], SEND_HOST, SEND_PORT, client_socket, i)
		#Release the thread lock
		thread_lock.release()
	
#Main function
def main():
	global client_buffer ,max_seq_number,client_socket,N,SEND_PORT,SEND_HOST,MSS

	#Variable intialization
	port = SEND_PORT
	host = SEND_HOST
	N = int(N)
	mss = int(MSS)
	
	#Read the data from the file to be sent over and break it into chunks based on MSS size provided
	#Store the chunkks in client_buffer based on the sequence number
	#Calculate the last sequence number
	sequence_number = 0
	try:
		with open(FILE_NAME, 'rb') as f:
			while True:
				chunk = f.read(int(mss))  
				if chunk:
					max_seq_number=sequence_number
					chunk_checksum=compute_checksum_for_chuck(chunk)
					client_buffer[sequence_number] = pickle.dumps([sequence_number,chunk_checksum,TYPE_DATA,chunk])
					sequence_number=sequence_number+1
				else:
					break
	except:
		sys.exit("Failed to open file!")

	#Initialize the signal thread that will help in timeout tracking
	signal.signal(signal.SIGALRM, timeout_thread)
	#Initialize the ack thread that will monitor the incoming ack's and sent the remaining packets
	ack_thread = threading.Thread(target=ack_process)
	ack_thread.start() 	
	#Do initial packet sending till the receipt of the acknowledgement from the receiver or sliding window is full
	rdt_send(client_buffer, client_socket, host, port)
	#Monitor if the sending is complete
	while 1:
		if sending_completed:
			break
	#blocks the main thread until the ack thread is terminated
	ack_thread.join()
	#close the socket
	client_socket.close()

if __name__ == "__main__":
    main()

