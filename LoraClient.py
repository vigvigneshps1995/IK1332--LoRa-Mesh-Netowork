import time
import json
import PyLora


# LoRA operating constants
LORA_FREQ = 866 * 1000000
LORA_BW = 125 * 1000
LORA_SF = 8
LORA_CR = 8
LORA_RECEIVE_TIMEOUT = 5 * 60        # in seconds


class LoraClient:

    def __init__(self, freq=LORA_FREQ, bw=LORA_BW, sf=LORA_SF, cr=LORA_CR, enable_crc=True):
        self.lora_client = PyLora
        self.lora_client.init()
        self.lora_client.set_frequency(freq)
        self.lora_client.set_bandwidth(bw)
        self.lora_client.set_coding_rate(cr)
        self.lora_client.set_spreading_factor(sf)
        if enable_crc:
            self.lora_client.enable_crc()
        else:
            self.lora_client.disable_crc()

    def send_payload(self, payload):
        try:
            print ("Sending payload: ")
            print (json.dumps(payload, indent=2))
            self.lora_client.send_packet(json.dumps(payload))
        except Exception as e:
            print ("Error sending message")
            print (str(e))

    def receive_payload(self, timeout=LORA_RECEIVE_TIMEOUT):
        payload = None
        t = time.time()
        try:
            self.lora_client.receive()      # put into receive mode
            while True:
                if self.lora_client.packet_available():
                    payload = self.lora_client.receive_packet()
                    break
                elif ((time.time() - t) > timeout):
                    raise Exception("Receive Timeout")
                time.sleep(0.1)
        except Exception as e:
            print ("Error receiving message")
            print (str(e))
        else:
            payload = json.loads(str(payload))
            print ("Payload Received: ")
            print (json.dumps(payload, indent=2))
        return payload


if __name__ == "__main__":
    from LoraClient import LoraClient
    c = LoraClient()
    while True:
        c.send_payload("hello")
        time.sleep(1)
