import socket
import sys


def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((sys.argv[1], int(sys.argv[2])))
	s.sendall(b'run')
	s.close()
	sys.exit(0)


if __name__ == "__main__":
	main()
