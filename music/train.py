import numpy as np
import tensorflow as tf
import pandas as pd
import msgpack
import glob
from tqdm import tqdm
import midi_manipulation
from tensorflow.python.ops import control_flow_ops

path="/home/ec2-user/ai/deeprap/music/blues"
files=glob.glob('{}/*.*mid*'.format(path))
songs=[]
for f in tqdm(files):
            song = np.array(midi_manipulation.midiToNoteStateMatrix(f))
            if np.array(song).shape[0] > 50:
                songs.append(song)

#MusicParams

lowestnote=midi_manipulation.lowerBound
highestnote=midi_manipulation.upperBound
noterange=highestnote-lowestnote


#Placeholders & vars for Network

x=tf.placeholder(tf.float32, [None, nv], name="x") #The placeholder for data
W=tf.Variable(tf.random_normal([nv, nh], 0.01), name="W")#weight matrix
bh=tf.Variable(tf.zeros([1, nh],  tf.float32, name="bh")) #bias for hidden layer
bv=tf.Variable(tf.zeros([1, nv],  tf.float32, name="bv")) #bias for visible layer




#Sampling helpers

def sample(probs):
    return tf.floor(probs+tf.random_uniform(tf.shape(probs), 0, 1))

def gibbs_step(count, k, xk):
        #Runs a single gibbs step. The visible values are initialized to xk
        hk=sample(tf.sigmoid(tf.matmul(xk, W) + bh))
        xk=sample(tf.sigmoid(tf.matmul(hk, tf.transpose(W)) + bv))
        return count+1, k, xk

def gibbs_sample(k):
    #Gibbs sample(done for k iterations) is used to approximate the distribution of the RBM(defined by W, bh, bv)
    ct=tf.constant(0)
    [_, _, x_sample]=control_flow_ops.while_loop(lambda count, num_iter, *args: count < num_iter,gibbs_step, [ct, tf.constant(k), x], parallel_iterations=1, back_prop=False)
    #to stop tensorflow from propagating gradients back through the gibbs step
    x_sample=tf.stop_gradient(x_sample)
    return x_sample

#backward pass, x samples drawn from prob distribution defn by (hk,w,bv)
x_sample=gibbs_sample(1)
#h sampled from prob distrib defn by (x,w,bh)
h=sample(tf.sigmoid(tf.matmul(x, W) + bh))
#h calculated from prob distrib defn by (x_sample,w,bh)
h_sample=sample(tf.sigmoid(tf.matmul(x_sample, W) + bh))


#contrastive divergence algorithm
#Update W, bh, and bv, based on the difference between the samples that are drawn and the original values
size_tr=tf.cast(tf.shape(x)[0], tf.float32)
eta=lr/size_tr
W_upd=tf.multiply(eta, tf.subtract(tf.matmul(tf.transpose(x), h), tf.matmul(tf.transpose(x_sample), h_sample)))
bv_upd=tf.multiply(eta, tf.reduce_sum(tf.subtract(x, x_sample), 0, True))
bh_upd=tf.multiply(eta, tf.reduce_sum(tf.subtract(h, h_sample), 0, True))
updt=[W.assign_add(W_upd), bv.assign_add(bv_upd), bh.assign_add(bh_upd)]


sess = tf.Session()
init = tf.initialize_all_variables()
sess.run(init)
for epoch in tqdm(range(epochs)):
            for song in songs:
                song = np.array(song)
                #reshaping song into chunks of timestep size
                chunks = song.shape[0]/timesteps
                dur = chunks*timesteps
                song = song[:dur]
                song = np.reshape(song, [chunks, song.shape[1]*timesteps])
                #Train the RBM on batch_size examples at a time
                for i in range(1, len(song), batch_size):
                    tr_x=song[i:i+batch_size]
                    sess.run(updt, feed_dict={x: tr_x})


#pickle.dump()
sample = gibbs_sample(1).eval(session=sess, feed_dict={x: np.zeros((10, nv))})
generatedfiles = []
for i in range(sample.shape[0]):
            if not any(sample[i,:]):
                continue
            #save the op vector as a midi file
            S = np.reshape(sample[i, :], (timesteps, 2*noterange))
            midi_manipulation.noteStateMatrixToMidi(S, "gen_snippet{}".format(i))
            generatedfiles.append("gen_snippet{}".format(i))
