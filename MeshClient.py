import json
import copy
import argparse
from LoraClient import LoraClient


# this is the format of message that is send across all the nodes
PAYLOAD_FORMAT = {
    "src": None                 # src device id
    "dst": None                 # dst device id
    "type": None                # type of payload (MSG/ACK/FLOOD)
    "payload": None             # payload
    "msg_id": None              # message counter
}

def send(node_id, lora_client):
    pass

def receive(node_id, lora_client):
    pass




class MeshClient:

    def __init__(self, node_id):
        self.node_id = node_id
        self.client = LoraClient()
        self.snd_buffer = []
        self.message_counter = 0

    def start(self):
        # while True:

            if len(self.snd_buffer) > 0:
                # send message to master client
                # send a mesage
                # wait for ack timeout
                # if ack timeout not received then send flood the network. 
 
            # # recevie a message 
            # payload = self.client.receive_payload()
            # # message with destination to this node
            # if payload['dst'] == self.node_id and payload['type'] != "MSG":
            #     # read message and send ack 
            #     pass
            # if payload['type'] == "FLOOD":
            #     # flood message here
            #     pass

       


if __name__ == "__main__":



