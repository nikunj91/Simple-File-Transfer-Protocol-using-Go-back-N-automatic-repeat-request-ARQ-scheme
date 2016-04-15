#Simple-FTP sender

import sys

def send_file(file_content, client_socket, host, port):
	print file_content

def main():
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
	
	try:
        file_content = []
        
        with open(file_name, 'rb') as f:
            while True:
                chunk = f.read(int(MSS))  
                if chunk:
                    file_content.append(chunk)
                else:
                    break
        print(file_content)
    except:
        sys.exit("Failed to open file!")
		
	send_file(file_content, client_socket, host, port)
	
	
if __name__ == "__main__":
    main()

