import socket
import os
from threading import Thread
import random
from datetime import datetime


ISMODIFIEDCLIENT = True

if ISMODIFIEDCLIENT:
	import webbrowser

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def main():
	try:
		import colorama
	except:
		print("Installing dependencies...")
		os.system("pip install colorama")

	from colorama import Fore, init, Back

	init()

	colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
		Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
		Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
		Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
	]

	client_colour = random.choice(colors)

	PORT = 6969
	SEPERATOR = "<SEP>"

	def yes_or_no(yes, no):
		ans = input("Would you like to host a room? (y/n) ")
		if ans == "y":
			yes()
		elif ans == "n":
			no()
		else:
			print("Invalid input.")
			yes_or_no(yes, no)

	def client(get_serv_ip = True, SERVER_IP = "127.0.0.1"):
		if get_serv_ip:
			SERVER_IP = input("What is the server IP? ")
		global serv
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print("[*] Connecting...")
		serv.connect((SERVER_IP, PORT))
		print("[+] Connected!")

		name = input("Enter your username: ")

		def listen_for_messages():
			while True:
				message = serv.recv(8092).decode()
				if message.find("%RICKROLL%") != -1 and ISMODIFIEDCLIENT:
					print('\n[*] You can disable this on line 8 by changing the True to False')
					webbrowser.open_new_tab("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
				else: print("\n" + message)

		t = Thread(target=listen_for_messages)
		t.daemon = True
		t.start()
		while True:
			to_send = input()
			print("\033[A\033[A")
			if to_send.lower() == 'q':
				serv.close()
				exit(0)
				break
			
			
			date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
			to_send = f"{client_colour}[{date_now}] {name}{SEPERATOR}{to_send}{Fore.RESET}"
			
			serv.send(to_send.encode())
		
	def server():
		global client_socks
		client_socks = set()
		global s
		s = socket.socket()
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(("0.0.0.0", PORT))
		s.listen(5)
		print(f"The IP is { socket.getfqdn() } or { get_ip() }")

		def listen_for_client(cs):
			while True:
				try:
					msg = cs.recv(8092).decode()
				except Exception as e:
					print(f"[!] Error: {e}")
					client_socks.remove(cs)

				else:
					msg = msg.replace(SEPERATOR, ": ")

				for client_socket in client_socks:
					client_socket.send(msg.encode())
		servclient = Thread(target=client, args=[False, "127.0.0.1"])
		servclient.daemon = True
		servclient.start()
		while True:
			client_sock, _ = s.accept()
			for client_socket in client_socks:
				client_socket.send("A user has joined.".encode('utf-8'))

			client_socks.add(client_sock)
			t = Thread(target=listen_for_client, args=(client_sock,))
			t.daemon = True
			t.start()
			if not servclient.is_alive:
				for sock in client_socks:
					sock.close()
				exit(0)

	yes_or_no(server, client)

if __name__ == "__main__":
	try:
		main()
	except:
		try:
			for cs in client_socks:
				cs.close()

			s.close()
			serv.close()
			exit(0)
		except: pass