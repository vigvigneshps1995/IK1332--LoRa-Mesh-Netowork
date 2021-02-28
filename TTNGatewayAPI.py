import time
import ttn

# constants
default_app_id = "kth-iotloramesh-26022021"
default_access_key = "ttn-account-v2.xWre66wLgzqM0ut1nICTkASjZgQXr666usHS8C7kYQE"


# class using mqtt client
class TTNGatewayAPI:
    def __init__(self, app_id=default_app_id, access_key=default_access_key):
        handler = ttn.HandlerClient(app_id, access_key)
        self.mqtt_client = handler.data()
        self.mqtt_client.connect()

    def send_to_ttn(self, dev_id, payload):
        self.mqtt_client.send(dev_id, payload)


if __name__ == "__main__":
    #using application manager client
    LoRAmash_gateway = TTNGatewayAPI()

    N = 10
    dev_id = "lora_pi1_test"
    payload = { "Hello from PI_5": "on", "counter": 1 }

    #print all the number from 0 to 9 (10 is excluded)
    for i in range(N):
            LoRAmash_gateway.send_to_ttn(dev_id, payload)
            time.sleep(3)
