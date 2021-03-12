import time
import json
import copy
import random
import argparse
import datetime
from threading import Thread
from multiprocessing import Process, Queue
from LoraClient import LoraClient

random.seed(1)

# this is the format of message that is send across all the nodes
PAYLOAD_FORMAT = {
    "src": None,                 # src device id
    "dst": None,                 # dst device id
    "payload": None,             # payload
}


def print_payload(payload):
    print ("\tMessage: %s -> %s\t\t%s\n" % (payload['src'], payload['dst'], payload['payload']))


def sender_thread(node_id, gw_id, send_q, recv_q, mode, temp_attached):
    while True:
        # format message to master client
        print ("Sending to gateway %s" % gw_id)
        send_msg = copy.deepcopy(PAYLOAD_FORMAT)
        send_msg["src"] = node_id
        send_msg["dst"] = gw_id
        if temp_attached:
            send_msg["payload"] = "%s : Hello from %s. Temperature in Celcius: %s" % (str(datetime.datetime.now()), node_id, str(read_temp()[0]))
        else:
            send_msg["payload"] = "%s : Hello from %s " % (str(datetime.datetime.now()), node_id)
        print_payload(send_msg)
        send_q.put(send_msg)
        # sleep for 30 seconds for next update
        time.sleep(2 + random.randint(1, 5))


def receiver_thread(node_id, gw_id, send_q, recv_q, mode, ttn_api=None):
    while True:
        # receive a message
        recv_msg = None
        if not recv_q.empty():
            recv_msg = recv_q.get()
        if recv_msg:
            if mode == "MASTER":
                print ("Message Received from %s" % recv_msg['src'])
                print_payload(recv_msg)
                ttn_api.send_to_ttn(recv_msg['src'], {"msg": recv_msg['payload']})
            if mode == "BRIDGE" and recv_msg['dst'] == node_id:
                print ("Bridging from %s to %s" % (recv_msg['src'], gw_id))
                # recv_msg['src'] = node_id
                recv_msg['dst'] = gw_id
                print_payload(recv_msg)
                send_q.put(recv_msg)


if __name__ == "__main__":

    # command line arguments
    parser = argparse.ArgumentParser(description='LoRa Mesh Client')
    parser.add_argument('--mode', required=True, help="The operating mode of the client. SLAVE | MASTER | BRIDGE ")
    parser.add_argument('--node-id', required=True, help="id assigned to node")
    parser.add_argument('--gateway-id', required=True, help="id of the gateway node")
    parser.add_argument('--temp', required=False, default=False, type=bool, help="id of the gateway node")
    args = parser.parse_args()

    # operating parameters
    node_id = args.node_id
    gw_id = args.gateway_id
    mode = args.mode
    temp_attached = False
    if args.temp:
        from Temperature import read_temp
        temp_attached = True

    # start the lora client process
    send_q, recv_q = Queue(), Queue()
    lora_client = LoraClient(send_q, recv_q)
    p = Process(target=lora_client.start_client)
    p.start()

    # start threads
    if mode == "SLAVE":
        print ("Starting mesh client in %s MODE" % mode)
        thread1 = Thread(target=sender_thread, args=(node_id, gw_id, send_q, recv_q, mode, temp_attached))
        thread1.start()
        thread1.join()
        p.join()

    if mode == "MASTER":
        print ("Starting mesh client in %s MODE" % mode)
        from TTNGatewayAPI import TTNGatewayAPI
        ttn_api = TTNGatewayAPI()
        thread1 = Thread(target=receiver_thread, args=(node_id, gw_id, send_q, recv_q, mode, ttn_api))
        thread1.start()
        thread1.join()
        p.join()

    if mode == "BRIDGE":
        print ("Starting mesh client in %s MODE" % mode)
        thread1 = Thread(target=sender_thread, args=(node_id, gw_id, send_q, recv_q, mode, temp_attached))
        thread2 = Thread(target=receiver_thread, args=(node_id, gw_id, send_q, recv_q, mode))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        p.join()

