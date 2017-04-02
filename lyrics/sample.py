from __future__ import absolute_import, division, print_function

import os
import pickle
from six.moves import urllib

import tflearn
import tensorflow as tf
import re
from tflearn.data_utils import *

path = "kanye_verses.txt"
maxlen = 20

def load_model():
    tf.reset_default_graph()

    if not os.path.isfile(path):
        print("No Input")
        exit()



    string_utf8 = open(path, "rU").read()
    string_utf8 = re.sub(r'[^\x00-\x7F]+', ' ', string_utf8)
    X, Y, char_idx = \
        string_to_semi_redundant_sequences(string_utf8, seq_maxlen=maxlen, redun_step=3)



    g = tflearn.input_data(shape=[None, maxlen, len(char_idx)])
    g = tflearn.lstm(g, 512, return_seq=True)
    g = tflearn.dropout(g, 0.5)
    g = tflearn.lstm(g, 512, return_seq=True)
    g = tflearn.dropout(g, 0.5)
    g = tflearn.lstm(g, 512)
    g = tflearn.dropout(g, 0.5)
    g = tflearn.fully_connected(g, len(char_idx), activation='softmax')
    g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                           learning_rate=0.001)

    m = tflearn.SequenceGenerator(g, dictionary=char_idx,
                                  seq_maxlen=maxlen,
                                  clip_gradients=5.0,
                                  checkpoint_path='checkpoints/deeprap')

    m.load("save/deeprap.tflearn")
    return m


def main():
    m = load_model()
    for i in range(1):
        seed = random_sequence_from_textfile(path, maxlen)
        print("-- TESTING...")
        print("-- Test with temperature of 1.0 --")
        print(m.generate(600, temperature=1.0, seq_seed=seed))
        print("-- Test with temperature of 0.5 --")
        print(m.generate(600, temperature=0.5, seq_seed=seed))

if __name__ == "__main__":
    main()