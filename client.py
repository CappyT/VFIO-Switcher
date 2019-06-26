import socket
import sys


def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((sys.argv[1], int(sys.argv[2])))
		s.sendall(b'run')
		s.close()
	except Exception as e:
		print("Exception occourred while connecting: " + str(e))
	sys.exit(0)


if __name__ == "__main__":
	main()
