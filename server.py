#Receiver side of the Go-back-N protocol

import sys

def main():
	# Read command line argument
	port = sys.argv[1]
    file_name = sys.argv[2]
    probability = sys.argv[3]
	
	port = int(port)
	probability = float(probability)
	
	#UDP socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	host = socket.gethostname()
	server_socket.bind((host, port)) 
	#while True:
		#data, addr = server_socket.recvfrom(1000000)
        #data = pickle.loads(data)
		#print data