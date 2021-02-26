import time
import json
import PyLora
from multiprocessing import Process, Queue


class LoraClient:

    # LoRA operating constants
    LORA_FREQ = 866 * 1000000
    LORA_BW = 125 * 1000
    LORA_SF = 8
    LORA_CR = 8

    def __init__(self, send_q, recv_q):
        self.lora_client = PyLora
        self.lora_client.init()
        self.lora_client.set_frequency(LoraClient_MP.LORA_FREQ)
        self.lora_client.set_bandwidth(LoraClient_MP.LORA_BW)
        self.lora_client.set_coding_rate(LoraClient_MP.LORA_CR)
        self.lora_client.set_spreading_factor(LoraClient_MP.LORA_SF)
        self.lora_client.enable_crc()

        # queues
        self.send_queue = send_q
        self.recv_queue = recv_q

    def start_client(self):
        self.lora_client.receive()      # always keep the lora in recevier mode
        while True:
            # send a packet if the packet is available
            try:
                while not self.send_queue.empty():
                    payload = self.send_queue.get()
                    #print ("Sending payload: ")
                    #print (json.dumps(payload, indent=2))
                    self.lora_client.send_packet(json.dumps(payload))
                    time.sleep(1)
            except Exception as e:
                print ("Error sending message")
                print (str(e))
            finally:
                self.lora_client.receive()      # put into receive mode

            # get a packet if it is available
            try:
                if self.lora_client.packet_available():
                    payload = json.loads(str(self.lora_client.receive_packet()))
                    self.recv_queue.put(payload)
                    #print ("Payload Received: ")
                    #print (json.dumps(payload, indent=2))
                    time.sleep(0.5)
            except Exception as e:
                print ("Error receiving message")
                print (str(e))


if __name__ == "__main__":

    send_q = Queue()
    recv_q = Queue()
    c = LoraClient_MP(send_q, recv_q)

    p = Process(target=c.start_client)
    p.start()
    while (True):
        send_q.put({"hello": "hi"})
        time.sleep(1)
    p.join()
