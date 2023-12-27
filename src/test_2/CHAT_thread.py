import queue
import socket
import threading
import time
import sys
from tkinter import *

# Adresy i porty każdego z "komputerów" (procesów)
# addresses = [(, 5000), (, 5001), (, 5002)]
addresses = ['192.168.43.155', '192.168.43.166', '192.168.43.111']
ports = [5000, 5001, 5002]

class RicartAgrawala:
    def __init__(self, my_id, total_processes):
        self.my_id = my_id
        self.total_processes = total_processes
        self.clock = 0

        self.reply_received = 0
        self.queue = []

        self.lock = threading.Lock()
        self.queue_lock = threading.Lock()

        self.sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(total_processes)]
        for i in range(total_processes):
            self.sockets[i].bind((addresses[self.my_id], ports[i]))
            threading.Thread(target=self.listen, args=(i,)).start()

    def request_cs(self):
        self.reply_received = 0
        self.broadcast_request()

        while self.reply_received < self.total_processes - 1:
            pass

        while min(self.queue, key=lambda x: x[1])[0] != self.my_id:
            pass

        print(f'QUEUE: {self.queue}')
        listbox.insert(END, f'QUEUE: {self.queue}')

        self.enter_cs()

    def broadcast_request(self):
        self.lock.acquire()

        self.queue_lock.acquire()
        self.queue.append((self.my_id, self.clock+1))
        self.queue_lock.release()

        for i in range(self.total_processes):
            if i != self.my_id:
                self.send_request(i)

        self.lock.release()

    def send_request(self, to):
        self.clock += 1
        message = f"REQUEST:{self.my_id}:{self.clock}"
        print(f"[{self.my_id}] - {self.clock} - Send REQUEST: {to}")
        self.sockets[to].sendto(message.encode('utf-8'), (addresses[to], ports[self.my_id]))

    def listen(self, from_id):
        print(f"[{self.my_id}] - {self.clock} - LISTEN: {from_id}")
        while True:
            data, addr = self.sockets[from_id].recvfrom(1024)
            if data:
                decoded_data = data.decode('utf-8')

                if decoded_data.startswith('RELEASE:'):
                    print(f"[{self.my_id}] - {self.clock + 1} - Receive RELEASE: {from_id}")
                    _, sender_id = decoded_data.split(':')
                    self.receive_release(int(sender_id))
                elif decoded_data.startswith("REQUEST:"):
                    print(f"[{self.my_id}] - {self.clock + 1} - Receive REQUEST: {from_id}")
                    _, sender_id, sender_clock = decoded_data.split(':')
                    self.receive_request(int(sender_id), int(sender_clock), addr)
                elif decoded_data.startswith("REPLY:"):
                    print(f"[{self.my_id}] - {self.clock + 1} - Receive REPLY: {from_id}")
                    self.receive_reply()

    def receive_request(self, from_id, timestamp, addr):
        self.lock.acquire()

        self.clock = max(self.clock, timestamp) + 1

        self.queue_lock.acquire()
        self.queue.append((from_id, timestamp))
        self.queue_lock.release()

        self.lock.release()

        self.lock.acquire()
        self.send_reply(from_id, addr)
        self.lock.release()

    def receive_reply(self):
        self.lock.acquire()
        self.clock += 1
        self.reply_received += 1
        self.lock.release()

    def receive_release(self, released_id):
        self.queue_lock.acquire()

        self.queue = [item for item in self.queue if item[0] != released_id]

        self.queue_lock.release()

    def send_reply(self, to, addr):
        self.clock += 1
        message = f"REPLY:{self.my_id}"
        print(f"[{self.my_id}] - {self.clock} - Send REPLY: {to}")
        self.sockets[to].sendto(message.encode('utf-8'), addr)

    def enter_cs(self):
        self.lock.acquire()
        self.clock += 1
        print(f"[{self.my_id}] - {self.clock} - ENTER CS")
        time.sleep(5)
        print(f"[{self.my_id}] - {self.clock} - EXIT CS")

        for i in range(self.total_processes):
            if i != self.my_id:
                self.send_release(i)

        self.lock.release()

    def send_release(self, to):
        self.queue_lock.acquire()

        message = f"RELEASE:{self.my_id}"
        self.sockets[to].sendto(message.encode('utf-8'), (addresses[to], ports[self.my_id]))
        self.queue = [item for item in self.queue if item[0] != self.my_id]

        self.queue_lock.release()


def main(my_id, total_processes, total_request):
    total_processes = len(addresses)
    processes = []

    # Tworzymy wątki reprezentujące różne procesy
    ra = RicartAgrawala(int(my_id), int(total_processes))
    time.sleep(3)
    for i in range(int(total_request)):
        ra.request_cs()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
