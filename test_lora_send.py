import PyLora
import argparse
import time



def send(lclient, t):
    sequence_num = 0
    while True:
        msg = 'Hello %s' % sequence_num
        lclient.send_packet(msg)
        print ("Sending " + msg)
        sequence_num += 1
        time.sleep(t)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sending Client for LoRa Client')
    parser.add_argument('--fq', required=False, help="The operating frequecy. Default= 868", type=int, default=868)
    parser.add_argument('--bw', required=False, help="Operating Bandwidth. Default= 125", type=int, default=125)
    parser.add_argument('--sf', required=False, help="Spreading Factor. Default = 12", type=int, default=12)
    parser.add_argument('--cr', required=False, help="Coding Rate, pass only the demonimator. Default = 4/5", type=int, default=5)
    parser.add_argument('--tx', required=False, help="Transmit Power. Default = 14dB", type=int, default=14)
    parser.add_argument('--crc', required=False, help="Enable/Disable CRC. Default = False", type=bool, default=False)
    parser.add_argument('--i', required=False, help="Interval between messages in seconds. Default = 10", type=int, default=10)
    args = parser.parse_args()

    lora_client = PyLora
    lora_client.init()
    lora_client.set_frequency(args.fq * 1000000)
    lora_client.set_bandwidth(args.bw * 1000)
    lora_client.set_spreading_factor(args.sf)
    lora_client.set_coding_rate(args.cr)
    lora_client.set_tx_power(args.tx)
    if args.crc:
        lora_client.enable_crc()
    else:
        lora_client.disable_crc()

    send(lora_client, args.i)
