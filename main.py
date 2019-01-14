import numpy as np
import pprint
import tensorflow as tf
import os
from datetime import datetime

from model import AlternatingAttention
import data_helper
import train
import test1
import sys

flags = tf.app.flags;

flags.DEFINE_integer("embedding_dim", 384, "Dimensionality of character embedding (default: 384)")
flags.DEFINE_integer("encoding_dim", 128, "Dimensionality of bidirectional GRU encoding for query / document")
flags.DEFINE_integer("num_glimpses", 8, "Number of glimpse iterations during read (default: 8)")
flags.DEFINE_float("dropout_keep_prob", 0.8, "Dropout keep probability (default: 0.8)")
flags.DEFINE_float("l2_reg_lambda", 1e-4, "L2 regularizaion lambda (default: 0.0001)")
flags.DEFINE_float("learning_rate", 1e-3, "AdamOptimizer learning rate (default: 0.001)")
flags.DEFINE_float("learning_rate_decay", 0.8, "How much learning rate will decay after half epoch of non-decreasing loss (default: 0.8)")

# Training parameters
flags.DEFINE_integer("batch_size", 1, "Batch Size (default: 32)")
flags.DEFINE_integer("num_epochs", 12, "Number of training epochs (default: 12)")
flags.DEFINE_integer("evaluate_every", 300, "Evaluate model on validation set after this many steps (default: 300)")

flags.DEFINE_boolean("trace", False, "Trace (load smaller dataset)")
flags.DEFINE_string("log_dir", "logs", "Directory for summary logs to be written to default (./logs/)")

flags.DEFINE_integer("checkpoint_every", 1000, "Save model after this many steps (default: 1000)")
flags.DEFINE_string("ckpt_dir", "./ckpts/", "Directory for checkpoints default (./ckpts/)")
flags.DEFINE_string("restore_file", "model-l3.165_a0.510.ckpt-11000", "Checkpoint to load")

flags.DEFINE_boolean("evaluate", True, "Whether to run evaluation epoch on a checkpoint. Must have restore_file set.")

def main(_):
    FLAGS = tf.app.flags.FLAGS
    pp = pprint.PrettyPrinter()
#    FLAGS._parse_flags()
    FLAGS(sys.argv)
    pp.pprint(FLAGS.__flags)

    # Load Data
    X_train, Q_train, Y_train = data_helper.load_data('train')
    X_test, Q_test, Y_test = data_helper.load_data('valid')

    vocab_size = np.max(X_train) + 1
    print('[?] Vocabulary Size:', vocab_size)

    # Create directories
    if not os.path.exists(FLAGS.ckpt_dir):
        os.makedirs(FLAGS.ckpt_dir)

    timestamp = str('\\') + datetime.now().strftime('%Y%m%d%H%M%S') 
    FLAGS.log_dir = str('log') + str(timestamp)
    print(FLAGS.log_dir)
    if not os.path.exists(FLAGS.log_dir):
        os.makedirs(FLAGS.log_dir)

    # Train Model
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, allow_soft_placement=True)) as sess, tf.device('/gpu:0'):
        model = AlternatingAttention(FLAGS.batch_size, vocab_size, FLAGS.encoding_dim, FLAGS.embedding_dim, FLAGS.num_glimpses, session=sess)

        if FLAGS.trace: # Trace model for debugging
            train.trace(FLAGS, sess, model, (X_train, Q_train, Y_train))
            return

        saver = tf.train.Saver()

        if FLAGS.restore_file is not None:
#            saver = tf.train.import_meta_graph('/tmp/model.ckpt.meta')
            saver = tf.train.import_meta_graph(str("./ckpts/")+str(FLAGS.restore_file))
            print('[?] Loading variables from checkpoint %s' % FLAGS.restore_file)
            saver.restore(sess, "./ckpts/model-l3.165_a0.510.ckpt-11000")
#            saver.restore(sess, FLAGS.restore_file)

        # Run evaluation
        if FLAGS.evaluate:
            if not FLAGS.restore_file:
                print('Need to specify a restore_file checkpoint to evaluate')
            else:
                test_data = data_helper.load_data('test')
                word2idx, _, _ = data_helper.build_vocab()
                test1.run(FLAGS, sess, model, test_data, word2idx)
        else:
            train.run(FLAGS, sess, model,
                    (X_train, Q_train, Y_train),
                    (X_test, Q_test, Y_test),
                    saver)

if __name__ == '__main__':
    tf.app.run()
