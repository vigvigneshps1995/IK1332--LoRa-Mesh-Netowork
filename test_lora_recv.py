import PyLora
import argparse
import time


def receive(lclient):
    while True:
        lclient.receive()   # put into receive mode
        while not lclient.packet_available():
            # wait for a package
            time.sleep(0.001)
        rec = lclient.receive_packet()
        print 'Packet received: %s. RSSI=%2f, SNR=%2f' % (rec, lclient.packet_rssi(), lclient.packet_snr())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sending Client for LoRa Client')
    parser.add_argument('--fq', required=False, help="The operating frequecy. Default= 868", type=int, default=868)
    parser.add_argument('--bw', required=False, help="Operating Bandwidth. Default= 125", type=int, default=125)
    parser.add_argument('--sf', required=False, help="Spreading Factor. Default = 12", type=int, default=12)
    parser.add_argument('--cr', required=False, help="Coding Rate, pass only the demonimator. Default = 4/5", type=int, default=5)
    parser.add_argument('--crc', required=False, help="Enable/Disable CRC. Default = False", type=bool, default=False)
    args = parser.parse_args()

    lora_client = PyLora
    lora_client.init()
    lora_client.set_frequency(args.fq * 1000000)
    lora_client.set_bandwidth(args.bw * 1000)
    lora_client.set_spreading_factor(args.sf)
    lora_client.set_coding_rate(args.cr)
    if args.crc:
        lora_client.enable_crc()
    else:
        lora_client.disable_crc()

    receive(lora_client)
