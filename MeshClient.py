import time
import json
import copy
import argparse
from threading import Thread
from LoraClient import LoraClient


# constants
READ_TIMEOUT = 2
ACK_TIMEOUT = 10

# global variables
lock = None
node_id = None
lora_client = None
message_counter = 0

# this is the format of message that is send across all the nodes
PAYLOAD_FORMAT = {
    "src": None,                 # src device id
    "dst": None,                 # dst device id
    "type": None,                # type of payload (MSG/ACK/FLOOD)
    "payload": None,             # payload
    "msg_id": None              # message counter
}

def acquire_lock(process_name):
    global lock
    while True:
        if lock is None:
	        lock = process_name
	        break
        time.sleep(0.1)        

def release_lock():
    global lock
    lock = None
    time.sleep(0.1)

def sender_thread():
    global node_id, lora_client, message_counter, master_node
    while True:
        acquire_lock("sender")
        print("Sender Thread")

        # format message to master client
        msg = copy.deepcopy(PAYLOAD_FORMAT)
        msg["src"] = node_id
        msg["dst"] = master_node
        msg["msg_id"] = message_counter
        msg["type"] = "MSG"
        msg["payload"] = "Hello from %s " % (node_id)
        lora_client.send_payload(msg)

        # wait for ack timeout and timeout
        ack_recevied = False
        t = time.time()
        ack = lora_client.receive_payload(timeout=ACK_TIMEOUT)
        if ack and ack['type'] == "ACK" and ack['msg_id'] == message_counter:
            ack_recevied = True

        # update message counter if ack is received
        if ack_recevied:
            print ("Ack for msg_id %s recevied" % message_counter)
            message_counter += 1

        # if ack timeout not received then flood the network.
        if not ack_recevied:
            print ("Ack Timeout for msg_id %s. FLOODING network" % message_counter)
            msg['type'] = "FLOOD"
            msg['msg_id'] = message_counter
            lora_client.send_payload(msg)
            message_counter += 1

        # send hello message every 5 seconds
        release_lock()
        time.sleep(10)

def receiver_thread():
    global node_id, lora_client, message_counter, master_node
    while True:
        acquire_lock("receiver")
        print("Receiver")

        # receive a message
        recv_msg = None
        try:
            recv_msg = lora_client.receive_payload(timeout=READ_TIMEOUT)
        except Exception("ReceiveTimeout"):
            pass

        # received message to this node so send ack
        if recv_msg:
            if recv_msg['type'] == "MSG" and recv_msg['dst'] == node_id:
                ack_msg = copy.deepcopy(PAYLOAD_FORMAT)
                ack_msg["src"] = node_id
                ack_msg["dst"] = recv_msg['src']
                ack_msg["msg_id"] = recv_msg['msg_id']
                ack_msg["type"] = "ACK"

                # send ack
                lora_client.send_payload(ack_msg)

            # flood request
            if recv_msg['type'] == "FLOOD":
                lora_client.send_payload(recv_msg)

        # release the lock on variables
        release_lock()


if __name__ == "__main__":

    global node_id, lora_client, message_counter, master_node
    node_id = "client-1"
    lora_client = LoraClient()
    message_counter = 0
    master_node = "client-3"

    thread1 = Thread(target=sender_thread, args=())
    thread2 = Thread(target=receiver_thread, args=())

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
