import threading
import socket
import time


class RicartAgrawala:
    def __init__(self, my_id, addresses, ports, gui):
        self.my_id = my_id
        self.total_processes = len(addresses)
        self.addresses = addresses
        self.ports = ports
        self.clock = 0

        self.reply_received = 0
        self.queue = []

        self.lock = threading.Lock()
        self.queue_lock = threading.Lock()

        self.gui = gui

        self.sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(self.total_processes)]
        for i in range(self.total_processes):
            print(i, self.addresses[self.my_id], self.ports[i])
            self.sockets[i].bind((self.addresses[self.my_id], self.ports[i]))
            threading.Thread(target=self.listen, args=(i,)).start()

    def request_cs(self, number_of_requests):
        for _ in range(int(number_of_requests)):
            self.reply_received = 0
            self.broadcast_request()

            while self.reply_received < self.total_processes - 1:
                pass

            while self.id_to_cs_enter() != self.my_id:
                pass

            print(f'QUEUE: {self.queue}')

            self.enter_cs()

    def id_to_cs_enter(self):
        min_clock = min(self.queue, key=lambda x: x[1])  # minimalny czas zegara
        min_list = [item for item in self.queue if item[1] == min_clock]  # lista procesow w konflikcie
        return min(min_list, key=lambda x: x[0])  # pierwszy wchodzi proces o nizszym ID

    def broadcast_request(self):
        self.lock.acquire()

        self.queue_lock.acquire()
        self.queue.append((self.my_id, self.clock))
        self.queue_lock.release()

        self.clock += 1
        for i in range(self.total_processes):
            if i != self.my_id:
                self.send_request(i)

        self.lock.release()

    def send_request(self, to):
        message = f"REQUEST:{self.my_id}:{self.clock}"

        log = f"Clock: {self.clock} - Send REQUEST: {to}"
        self.gui.data.insert('end', log)
        self.gui.data.itemconfig(len(self.gui.data.get(0, 'end')) - 1, {'bg': '#F0DA32'})

        self.sockets[to].sendto(message.encode('utf-8'), (self.addresses[to], self.ports[self.my_id]))

    def listen(self, from_id):
        self.gui.log_listen(self.clock, from_id)
        while True:
            data, addr = self.sockets[from_id].recvfrom(1024)
            if data:
                decoded_data = data.decode('utf-8')
                if decoded_data.startswith('RELEASE:'):
                    self.gui.log_receive(self.clock, from_id, "RELEASE")
                    _, sender_id = decoded_data.split(':')
                    self.receive_release(int(sender_id))
                elif decoded_data.startswith("REQUEST:"):
                    self.gui.log_receive(self.clock, from_id, "REQUEST")
                    _, sender_id, sender_clock = decoded_data.split(':')
                    self.receive_request(int(sender_id), int(sender_clock), addr)
                elif decoded_data.startswith("REPLY:"):
                    self.gui.log_receive(self.clock, from_id, "REPLY")
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
        # self.clock += 1
        message = f"REPLY:{self.my_id}"
        # self.gui.log_send_reply(self.clock, to)

        log = f"Clock: {self.clock} - Send REPLY: {to}"
        print(log)
        self.gui.data.insert('end', log)
        self.gui.data.itemconfig(len(self.gui.data.get(0, 'end')) - 1, {'bg': '#3894F0'})

        self.sockets[to].sendto(message.encode('utf-8'), addr)

    def enter_cs(self):
        self.lock.acquire()
        self.clock += 1
        self.gui.log_cs(self.clock, "ENTER")
        time.sleep(5)
        self.clock += 1
        self.gui.log_cs(self.clock, "EXIT")

        for i in range(self.total_processes):
            if i != self.my_id:
                self.send_release(i)

        self.lock.release()

    def send_release(self, to):
        self.queue_lock.acquire()

        message = f"RELEASE:{self.my_id}"
        self.sockets[to].sendto(message.encode('utf-8'), (self.addresses[to], self.ports[self.my_id]))
        self.queue = [item for item in self.queue if item[0] != self.my_id]

        self.queue_lock.release()
