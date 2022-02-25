import argparse
import numpy as np
import os
import collections
from os.path import dirname, abspath
from copy import deepcopy
from sacred import Experiment, SETTINGS
from sacred.observers import FileStorageObserver
from sacred.utils import apply_backspaces_and_linefeeds
import sys
import torch as th
from utils.logging import get_logger
import yaml
import datetime

from run import run


SETTINGS['CAPTURE_MODE'] = "fd" # set to "no" if you want to see stdout/stderr in console
SETTINGS.CONFIG.READ_ONLY_CONFIG = False # allow to change configs after the experiment is initialized

logger = get_logger()

ex = Experiment("pymarl")
ex.logger = logger
ex.captured_out_filter = apply_backspaces_and_linefeeds

results_path = os.path.join(dirname(dirname(abspath(__file__))), "results")


@ex.main
def my_main(_run, _config, _log, env_args):
    # Setting the random seed of the environment
    print('my_main')
    env_args['seed'] = _config["seed"]

    # run the framework
    run(_run, _config, _log)


def _get_config(config_name, subfolder):
    with open(os.path.join(os.path.dirname(__file__), "config", subfolder, "{}.yaml".format(config_name)), "r") as f:
        try:
            config_dict = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert False, "{}.yaml error: {}".format(config_name, exc)
    return config_dict


def recursive_dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = recursive_dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


if __name__ == '__main__':
    # delete arguments from sys.argv
    params = deepcopy(sys.argv)[0]
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-config", default="sc2", type=str) # Environment config
    parser.add_argument("--config", default="liir_smac", type=str) # Algorithm config
    parser.add_argument("--map", default="", type=str) # Map name
    args = parser.parse_args()

    # Get the defaults from default.yaml
    with open(os.path.join(os.path.dirname(__file__), "config", "default.yaml"), "r") as f:
        try:
            config_dict = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert False, "default.yaml error: {}".format(exc)
    # Load algorithm and env base configs
    env_config = _get_config(args.env_config, "envs")
    alg_config = _get_config(args.config, "algs")
    config_dict = recursive_dict_update(config_dict, env_config)
    config_dict = recursive_dict_update(config_dict, alg_config)
    
    # specify the map for experiment

    if args.map == "":
        map_name = config_dict['env_args']['map_name']
    else:
        map_name = args.map
        config_dict['env_args']['map_name'] = map_name
    # now add all the config to sacred
    print(params)
    ex.add_config(config_dict)


    # Save to disk by default for sacred
    unique_token = "{}_{}_{}".format(config_dict['name'], map_name, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    logger.info("Saving to FileStorageObserver in results/sacred/{}/.".format(unique_token))
    file_obs_path = os.path.join(results_path, "sacred", unique_token)
    ex.observers.append(FileStorageObserver.create(file_obs_path))
    ex.run_commandline(params)
