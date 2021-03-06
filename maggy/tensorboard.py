"""
Module to encapsulate functionality related to writing to the tensorboard
log dir and programmatically structure the outputs.
"""

import tensorflow.compat.v2 as tf
from tensorboard.plugins.hparams import summary_v2 as hp
from tensorboard.plugins.hparams import api_pb2
from tensorboard.plugins.hparams import summary

__import__("tensorflow").compat.v1.enable_eager_execution()

_tensorboard_dir = None
_writer = None


def _register(trial_dir):
    global _tensorboard_dir
    global _writer
    _tensorboard_dir = trial_dir
    _writer = tf.summary.create_file_writer(_tensorboard_dir)


def logdir():
    """Returns the path to the tensorboard log directory.

    Instead of hardcoding a log dir path in a training function, users should
    make use of this function call, which will programmatically create a folder
    structure for tensorboard to visualize the machine learning experiment.

    :return: Path of the log directory in HOPSFS
    :rtype: str
    """
    global _tensorboard_dir
    return _tensorboard_dir


def _create_hparams_config(searchspace):
    hparams = []

    for key, val in searchspace.names().items():
        if val == "DOUBLE":
            hparams.append(
                hp.HParam(
                    key,
                    hp.RealInterval(
                        float(searchspace.get(key)[0]), float(searchspace.get(key)[1])
                    ),
                )
            )
        elif val == "INTEGER":
            hparams.append(
                hp.HParam(
                    key,
                    hp.IntInterval(searchspace.get(key)[0], searchspace.get(key)[1]),
                )
            )
        elif val == "DISCRETE":
            hparams.append(hp.HParam(key, hp.Discrete(searchspace.get(key))))
        elif val == "CATEGORICAL":
            hparams.append(hp.HParam(key, hp.Discrete(searchspace.get(key))))

    return hparams


def _write_hparams_config(log_dir, searchspace):
    HPARAMS = _create_hparams_config(searchspace)
    METRICS = [
        hp.Metric("epoch_acc", group="validation", display_name="accuracy (val.)",),
        hp.Metric("epoch_loss", group="validation", display_name="loss (val.)",),
        hp.Metric("epoch_acc", group="train", display_name="accuracy (train)",),
        hp.Metric("epoch_loss", group="train", display_name="loss (train)",),
    ]

    with tf.summary.create_file_writer(log_dir).as_default():
        hp.hparams_config(hparams=HPARAMS, metrics=METRICS)


def _write_hparams(hparams, trial_id):
    global _writer
    with _writer.as_default():
        hp.hparams(hparams, trial_id)


def _write_session_end():
    global _writer
    with _writer.as_default():
        protob = summary.session_end_pb(api_pb2.STATUS_SUCCESS)
        raw_pb = protob.SerializeToString()
        tf.summary.experimental.write_raw_pb(raw_pb, step=0)
    _writer = None
