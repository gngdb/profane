# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['RCDIR', 'get_rcdir', 'parse_args', 'setup', 'get_config', 'create_dirs', 'SyncLocalCallback', 'SyncSharedCallback',
           'init', 'parse_output_log']

# %% ../nbs/00_core.ipynb 3
import argparse
from pathlib import Path

# this is used for testing
RCDIR = None

def get_rcdir():
    """Function to get the rcdir."""
    rcdir = RCDIR or Path.home()
    if isinstance(rcdir, str):
        rcdir = Path(rcdir)
    return rcdir

def parse_args():
    argument_parser = argparse.ArgumentParser("Set up a ~/.profanerc file and register the required directories.")
    argument_parser.add_argument('local_storage', type=Path, help="The local storage directory, everything will be stored here.")
    argument_parser.add_argument('shared_storage', type=Path, help="The shared storage directory, only the terminal logs and metadata will be stored here.")
    argument_parser.add_argument('--user', type=str, default=None, help="Optional: The user name to use for the shared storage directory.")
    return argument_parser.parse_args()

def setup():
    args = parse_args() 
    return _setup(args.local_storage, args.shared_storage, args.user)

def _setup(local_storage, shared_storage, user):
    """Function to set up the ~/.profanerc file and register the required directories."""
    # check the two directories exist
    if not local_storage.exists():
        raise FileNotFoundError(f"{local_storage} does not exist.")
    if not shared_storage.exists():
        raise FileNotFoundError(f"{shared_storage} does not exist.")
    # save the config file
    rcdir = get_rcdir()
    config_file = rcdir / ".profanerc"
    config_file.write_text(f"local_storage={str(local_storage.resolve())}\nshared_storage={str(shared_storage.resolve())}" + (f"\nuser={user}" if user else ""))

def get_config():
    """Function to get the config file."""
    rcdir = get_rcdir()
    config_file = rcdir / ".profanerc"
    if not config_file.exists():
        raise FileNotFoundError(f"{config_file} does not exist. Run profane_setup <local dir> <shared dir> to set it up.")
    config = {}
    for line in config_file.read_text().splitlines():
        key, value = line.split("=")
        config[key] = value
    return config

# %% ../nbs/00_core.ipynb 4
import wandb
# from typing import Callable, NamedTuple
from enum import IntEnum
import shutil
from distutils.dir_util import copy_tree
import os
import atexit
from wandb.sdk.wandb_run import TeardownHook, TeardownStage
import time

# create directories using run information
def create_dirs(run_id, user, project):
    config = get_config()
    if len(project) == 0:
        project = "misc"
    shared_dir = Path(config['shared_storage']) / user / project / run_id
    shared_dir.mkdir(parents=True)
    local_dir = Path(config['local_storage']) / project / run_id
    local_dir.mkdir(parents=True)
    return shared_dir, local_dir


class SyncLocalCallback:
    def __init__(self):
        self.exited = False

    def register_dirs(self, local_dir, wandb_dir):
        self.local_dir = local_dir
        self.wandb_dir = wandb_dir

    def __call__(self):
        print("local callback called")
        if not self.exited:
            # if dir is empty sleep
            while len([p for p in self.wandb_dir.iterdir()]) < 1:
                time.sleep(1)
                print(f"waiting for {self.wandb_dir} to be populated")
            print(f"found {len([p for p in self.wandb_dir.iterdir()])} files in {self.wandb_dir}")
            # copy wandb dir to shared dir, nothing fancy
            # copy_tree(str(self.wandb_dir), str(self.local_dir), verbose=1)
            for path_object in self.wandb_dir.rglob('*'):
                if path_object.is_file():
                    print(f"copying {path_object} to {self.local_dir / path_object.relative_to(self.wandb_dir)}")
                    shutil.copy(path_object, self.local_dir / path_object.relative_to(self.wandb_dir))
                else:
                    (self.local_dir / path_object.relative_to(self.wandb_dir)).mkdir(parents=True, exist_ok=True)
            print(f"copied {self.wandb_dir} to {self.local_dir}")
            self.exited = True

       
class SyncSharedCallback:
    def __init__(self):
        self.exited = False

    def register_dirs(self, shared_dir, wandb_dir):
        self.shared_dir = shared_dir
        self.wandb_dir = wandb_dir

    def __call__(self):
        print("shared callback called")
        if not self.exited:
            # find the wandb output file:
            for path_object in self.wandb_dir.rglob('*'):
                if path_object.is_file():
                    if path_object.suffix == '.wandb':
                        wandb_file = path_object
                        break
            # parse the wandb file
            output_log = parse_output_log(wandb_file)
            # write output log to shared_dir
            with open(self.shared_dir / 'output.log', 'w') as f:
                f.write(output_log)
            # this should be where the metadata is
            metadata_file = self.wandb_dir / "files/wandb-metadata.json"
            # copy metadata file and write output log
            shutil.copy(metadata_file, self.shared_dir)
            print(f"file written to {self.shared_dir / 'output.log'}")
            self.exited = True
 

def init(**kwargs):
    """
    A wrapper for `wandb.init`.
    """
    # atexit called in reverse order so these need to be created first
    local_hook = SyncLocalCallback()
    shared_hook = SyncSharedCallback()

    kwargs['mode'] = 'offline'
    run = wandb.init(**kwargs)
    config = get_config()
    wandb_dir = Path(run.dir).parent
    username = os.environ['USER'] if 'user' not in config else config['user']
    shared_dir, local_dir = create_dirs(run.id, username, run.project)
    shared_hook.register_dirs(shared_dir, wandb_dir)
    local_hook.register_dirs(local_dir, wandb_dir)
    # this will trigger if run.finish() is called
    run._teardown_hooks += [TeardownHook(local_hook, TeardownStage.LATE),
                            TeardownHook(shared_hook, TeardownStage.LATE)]
    def finish():
        print("finish called")
        run.finish()
        local_hook()
        shared_hook()
    atexit.register(finish)
    return run

# %% ../nbs/00_core.ipynb 5
from wandb.proto import wandb_internal_pb2
from wandb.sdk.internal import datastore


def parse_output_log(data_path):
    """
    Parse wandb data from a given path.
    Returns the terminal log typically saved as `output.log`,
    which isn't created unless you're running in online mode.
    But, the data still exists in the `.wandb` file.
    """
    # https://github.com/wandb/wandb/issues/1768#issuecomment-976786476 
    ds = datastore.DataStore()
    ds.open_for_scan(data_path)
    terminal_log = []

    data = ds.scan_record()
    while data is not None:
        pb = wandb_internal_pb2.Record()
        pb.ParseFromString(data[1])  
        record_type = pb.WhichOneof("record_type")
        if record_type == "output_raw":
            terminal_log.append(pb.output_raw.line)
            #print(pb.output_raw)
        data = ds.scan_record()
    return "".join(terminal_log)
