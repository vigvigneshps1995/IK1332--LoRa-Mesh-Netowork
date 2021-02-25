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
operating_mode = None
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


def print_payload(payload):
    print ("\tMessage: %s -> %s [type=%s] [id=%s] %s " % (payload['src'], payload['dst'], payload['type'], payload['msg_id'], payload['msg_id']))


def sender_thread():
    global node_id, lora_client, message_counter, master_node, operating_mode
    while True:
        acquire_lock("sender")
        print("Sender thread")

        # format message to master client
        msg = copy.deepcopy(PAYLOAD_FORMAT)
        msg["src"] = node_id
        msg["dst"] = master_node
        msg["msg_id"] = message_counter
        msg["type"] = "MSG"
        msg["payload"] = "%s : Hello from %s " % (str(datetime.datetime.now()), node_id)
        print ("Sending to master ...")
        print_payload(msg)
        lora_client.send_payload(msg)

        # wait for ack timeout and timeout
        ack_recevied = False
        ack = lora_client.receive_payload(timeout=ACK_TIMEOUT)
        if ack and (ack['type'] == "ACK") and (ack['src'] == master_node) and (ack['dst'] == node_id) and (ack['msg_id'] == message_counter):
            ack_recevied = True

        # update message counter if ack is received
        if ack_recevied:
            print ("Ack for msg_id %s recevied" % message_counter)
            print_payload(msg)
            message_counter += 1

        # if ack timeout not received then flood the network.
        if not ack_recevied:
            msg['type'] = "FLOOD"
            msg['msg_id'] = message_counter
            print ("Ack Timeout for msg_id %s. FLOODING network" % message_counter)
            print_payload(msg)
            lora_client.send_payload(msg)
            message_counter += 1
            time.sleep(3)           # so all the floods msg are cleared

        # send hello message every 30 seconds
        print;print;
        release_lock()
        time.sleep(30)


def receiver_thread():
    global node_id, lora_client, message_counter, master_node, operating_mode
    while True:
        acquire_lock("receiver")
        print("Receiver thread")

        # receive a message
        recv_msg = None
        try:
            recv_msg = lora_client.receive_payload(timeout=READ_TIMEOUT)
        except Exception("ReceiveTimeout"):
            pass

        # received message to this node so send ack
        if recv_msg:
            if recv_msg['type'] == "MSG" and recv_msg['dst'] == node_id:
                print ("Message Received ...")
                print_payload(recv_msg)

                ack_msg = copy.deepcopy(PAYLOAD_FORMAT)
                ack_msg["src"] = node_id
                ack_msg["dst"] = recv_msg['src']
                ack_msg["msg_id"] = recv_msg['msg_id']
                ack_msg["type"] = "ACK"

                # send ack
                print ("Sending Ack ...")
                print_payload(ack_msg)
                lora_client.send_payload(ack_msg)

            # flood request
            if operating_mode != "MASTER":
                if recv_msg['src'] != node_id and recv_msg['type'] == "FLOOD":
                    print ("Request for flood ... Flooding ...")
                    print_payload(recv_msg)
                    lora_client.send_payload(recv_msg)

        # release the lock on variables
        print;print;
        release_lock()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='LoRa Mesh Client')
    parser.add_argument('--node-id', required=True, help="id assigned to node")
    parser.add_argument('--gateway-id', required=False, default=None, help="id of the gateway node")
    args = parser.parse_args()

    node_id = args.node_id
    master_node = args.gateway_id
    message_counter = 0
    lora_client = LoraClient()

    if master_node:
        operating_mode = 'CLIENT'
        print ("Starting mesh client in %s MODE" % operating_mode)
        thread1 = Thread(target=sender_thread, args=())
        thread2 = Thread(target=receiver_thread, args=())
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
    else:
        operating_mode = 'MASTER'
        print ("Starting mesh client in %s MODE" % operating_mode)
        thread1 = Thread(target=receiver_thread, args=())
        thread1.start()
        thread1.join()
