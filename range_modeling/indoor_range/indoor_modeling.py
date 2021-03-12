import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np


if __name__ == "__main__":
    Ptx = 14
    f = 868 * 1000000
    c = 3 * 100000000
    
    ref_loss = 20 * math.log((4*math.pi*f/c) , 10)

    # adjacent room 
    room_d = 4 
    a_w = 12    #  4 inch concrete
    room_rec_sig, room_distance = [], []
    i = 1.0
    while i < 30:
        n_w = i // room_d + 1    
        motley_keenan_loss = ref_loss + 20 * math.log(i, 10) + (n_w * a_w) 
        recieved_signal = Ptx - motley_keenan_loss
        room_rec_sig.append(recieved_signal)
        room_distance.append(i)
        i += .1

    # floors 
    floor_d = 3 
    a_f = 14    # brick and concrete 8 inch 
    floor_rec_sig, floor_distance = [], []
    i = 1.0
    while i < 30:
        n_f = i // floor_d + 1
        motley_keenan_loss = ref_loss + 20 * math.log(i, 10) + (n_f * a_f)
        recieved_signal = Ptx - motley_keenan_loss
        floor_rec_sig.append(recieved_signal)
        floor_distance.append(i)
        i += .1


    # plot diagrams
    fig, ax = plt.subplots(figsize=(10, 5)) 
    ax.plot(floor_distance, floor_rec_sig, c='r', linewidth=1, label="received signal strength across floors (dB)")
    ax.plot(room_distance, room_rec_sig, c='g', linewidth=1, label="received signal strength across adjacent rooms (dB)")
    ax.plot([0, 30], [-137, -137], c='b', linestyle="--",linewidth=2, label="receiver sensitivity (dB)")
    ax.set(xlabel='distance (m)', ylabel='received signal (dB)', title='Signal propagation in a indoor building')
    ax.grid()
    ax.set_xticks([3, 6, 9, 12, 15, 18, 21, 24, 27, 30])
    ax.legend()
    plt.show()
