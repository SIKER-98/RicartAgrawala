import sys
import threading
import tkinter as tk
from multiprocessing import Process
from threading import Thread
from tkinter import *
from RicartAgrawala import RicartAgrawala


class GUI:

    def __init__(self, my_id):
        self.ra = None
        self.my_id = my_id

        self.root = tk.Tk()

        self.addresses = tk.StringVar()
        self.ports = tk.StringVar()
        self.numberOfRequest = tk.IntVar()

        self.lock = threading.Lock()

        self.requests = []
        self.history = []

        self.addresses_label = tk.Label(self.root, text="Addresses:", font=('calibre', 10, 'bold'))
        self.addresses_entry = tk.Entry(self.root, textvariable=self.addresses, font=('calibre', 10, 'normal'))
        self.addresses_entry.insert(0, '192.168.0.245 192.168.0.163 192.168.0.10')

        self.port_label = tk.Label(self.root, text="Ports:", font=('calibre', 10, 'bold'))
        self.port_entry = tk.Entry(self.root, textvariable=self.ports, font=('calibre', 10, 'normal'))
        self.port_entry.insert(0, "5000 5001 5002")

        self.request_label = tk.Label(self.root, text="Request:", font=('calibre', 10, 'bold'))
        self.request_entry = tk.Entry(self.root, textvariable=self.numberOfRequest, font=('calibre', 10, 'normal'))
        self.request_entry.insert(0, '3')

        self.run_button = tk.Button(self.root, text="RUN", command=self.run_algorithm)
        self.clear_button = tk.Button(self.root, text="CLEAR HISTORY", command=self.clear_history)
        self.request_button = tk.Button(self.root, text="REQUEST", command=self.send_request)

        self.data = tk.Listbox(self.root)
        self.data = tk.Listbox(self.root, width=70, height=15)
        self.scrollbar = tk.Scrollbar(self.root)
        self.data.config(yscrollcommand=self.scrollbar.set)

        self.addresses_label.grid(row=0, column=0, sticky='nesw')
        self.addresses_entry.grid(row=0, column=1, sticky='nesw')
        self.port_label.grid(row=1, column=0, sticky='nesw')
        self.port_entry.grid(row=1, column=1, sticky='nesw')
        self.request_label.grid(row=2, column=0, sticky='nesw')
        self.request_entry.grid(row=2, column=1, sticky='nesw')

        self.run_button.grid(row=3, column=0, columnspan=2, sticky='nesw')
        self.clear_button.grid(row=4, column=0, columnspan=2, sticky='nesw')
        self.request_button.grid(row=5, column=0, columnspan=2, sticky='nesw')

        self.data.grid(row=6, column=0, columnspan=2, sticky='nsew')
        self.data.columnconfigure(0, weight=1)

        self.scrollbar.grid(row=6, column=2, sticky='ns')

    def run_algorithm(self):
        addresses = self.addresses_entry.get().split(' ')
        port = [int(port) for port in self.port_entry.get().split(' ')]

        print(addresses)
        print(port)

        self.ra = RicartAgrawala(self.my_id, addresses, port, self)

    def send_request(self):
        process = Thread(target=self.ra.request_cs, args=(self.request_entry.get(),))
        process.start()

    def clear_history(self):
        self.data.delete(0, 'end')

    def log_listen(self,clock, from_id):
        self.lock.acquire()
        log = f"Clock: {clock} - LISTEN: {from_id}"
        print(log)
        self.data.insert('end', log)
        self.lock.release()

    def log_receive(self, clock, from_id, type):
        self.lock.acquire()
        log = f"Clock: {clock} - Receive {type}: {from_id}"
        print(log)
        self.data.insert('end', log)
        self.data.itemconfig(len(self.data.get(0, 'end')) - 1, {'bg': '#F06F26'})
        self.lock.release()

    def log_cs(self, clock, type):
        self.lock.acquire()
        log = f"Clock: {clock} - {type} CS"
        print(log)
        self.data.insert('end', log)
        self.data.itemconfig(len(self.data.get(0, 'end')) - 1, {'bg': '#F013ED'})
        self.lock.release()

    def start(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = GUI(int(sys.argv[1]))
    gui.start()
