from flask import Flask
import pronouncing
import random
import rearrange
import os
import re
#import lyrics.sample as lyrics_sample
#import music

import tflearn
import tensorflow as tf
from tflearn.data_utils import *



app = Flask(__name__)
m_lyrics = None
maxlen = 20
path = '/music/kanye_verses.txt'

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/lyrics")
def lyrics():

    seed = random_sequence_from_textfile(path, maxlen)
    print(m_lyrics.generate(60, temperature=0.8, seq_seed=seed))
    return jsonify(lyrics=lyrics)


def load_lyrics_model():
    path = "lyrics/kanye_verses.txt"
    maxlen = 20

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

    m.load("lyrics/save/deeprap.tflearn")
    return m




if __name__ == "__main__":
    m_lyrics = load_lyrics_model()
    app.run()
