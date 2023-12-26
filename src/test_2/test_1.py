import multiprocessing
import socket
import threading
import time

# Adresy i porty każdego z "komputerów" (procesów)
addresses = [('localhost', 5000), ('localhost', 5001), ('localhost', 5002), ('localhost', 5003)]
LOCK = threading.Lock()


class RicartAgrawala:
    def __init__(self, id, total_processes):
        global LOCK

        self.my_id = id
        self.total_processes = total_processes
        self.timestamp = 0
        self.events = []
        self.queue = []
        self.lock = threading.Lock
        self.reply = 0

        self.sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        for i in range(total_processes)]

        for i, (host, port) in enumerate(addresses):
            if i != self.my_id:
                self.sockets[i].bind((host, port))
                threading.Thread(target=self.listen, args=(i,)).start()

    def request_cs(self):
        print("Requesting")

    # broadcast REQUEST
    def broadcast_request(self):
        print("Broadcasting request")

    # send REQUEST to
    def send_request(self):
        print("Sending request")

    # listen for on port
    def listen(self, id):
        print(f"[{self.my_id}]: Listening proccess {id}")

        while True:
            data, addr = self.sockets[id].recvfrom(1024)
            print(f"[{id}] Received from {id} - {data}")

            if data:
                decoded_data = data.decode('utf-8')


    # receive REQUEST
    def receive_request(self):
        print("Receiving")

    # receive REPLY
    def send_reply(self):
        print("Sending reply")

    # enter CS
    def enter_cs(self):
        print("Entering")


def simulate_process(process_id, ricart_agrawala):
    # Symulacja pracy procesu
    time.sleep(process_id)
    ricart_agrawala.request_cs()


def main():
    total_processes = 4
    processes = []

    ra = RicartAgrawala(0, total_processes)  # Tworzymy instancję algorytmu Ricart-Agrawala

    # Tworzymy wątki reprezentujące różne procesy
    for i in range(total_processes):
        process = threading.Thread(target=simulate_process, args=(i, ra))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
