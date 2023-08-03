# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['RCDIR', 'logger', 'get_rcdir', 'parse_args', 'setup', 'write_profanerc', 'get_config', 'iterate_records',
           'parse_output_log', 'parse_stats', 'create_dirs', 'SyncLocalCallback', 'SyncSharedCallback',
           'system_to_string', 'git_patch_callback', 'git_status', 'git_branch', 'init']

# %% ../nbs/00_core.ipynb 3
import argparse
from pathlib import Path

# this is used for testing
RCDIR = None

def get_rcdir():
    """Function to get the rcdir. Returns `Path` object of the rcdir."""
    rcdir = RCDIR or Path.home()
    if isinstance(rcdir, str):
        rcdir = Path(rcdir)
    return rcdir

# %% ../nbs/00_core.ipynb 4
def parse_args():
    argument_callback = argparse.ArgumentParser("Set up a ~/.profanerc file and register the required directories.")
    argument_callback.add_argument('local_storage', type=Path, help="The local storage directory, everything will be stored here.")
    argument_callback.add_argument('shared_storage', type=Path, help="The shared storage directory, only the terminal logs and metadata will be stored here.")
    argument_callback.add_argument('--user', type=str, default=None, help="Optional: The user name to use for the shared storage directory.")
    return argument_callback.parse_args()

# %% ../nbs/00_core.ipynb 5
def setup():
    """Parses args and calls write_profanerc()"""
    args = parse_args() 
    return write_profanerc(args.local_storage, args.shared_storage, args.user)

# %% ../nbs/00_core.ipynb 6
def write_profanerc(local_storage, shared_storage, user):
    """
    Function to set up the ~/.profanerc file and register the required directories.
    Example ~/.profanerc file that will be written:
    ```
        local_storage=/home/user/profane/local_storage
        shared_storage=/home/user/profane/shared_storage
        user=me
    ```
    """
    # check the two directories exist
    if not local_storage.exists():
        raise FileNotFoundError(f"{local_storage} does not exist.")
    if not shared_storage.exists():
        raise FileNotFoundError(f"{shared_storage} does not exist.")
    # save the config file
    rcdir = get_rcdir()
    config_file = rcdir / ".profanerc"
    config_file.write_text(f"local_storage={str(local_storage.resolve())}\nshared_storage={str(shared_storage.resolve())}" + (f"\nuser={user}" if user else ""))

# %% ../nbs/00_core.ipynb 7
def get_config():
    """
    Function to load the config from the ~/.profanerc file.
    Loads the config as a dictionary and returns it.
    Example ~/.profanerc file to load from:
    ```
        local_storage=/home/user/profane/local_storage
        shared_storage=/home/user/profane/shared_storage
        user=me
    ```
    Example config dictionary:
    ```
       {'local_storage': '/home/user/profane/local_storage',
        'shared_storage': '/home/user/profane/shared_storage',
        'user': 'me'}
    ```
    """
    rcdir = get_rcdir()
    config_file = rcdir / ".profanerc"
    if not config_file.exists():
        raise FileNotFoundError(f"{config_file} does not exist. Run profanewrite_profanerc <local dir> <shared dir> to set it up.")
    config = {}
    for line in config_file.read_text().splitlines():
        key, value = line.split("=")
        config[key] = value
    return config

# %% ../nbs/00_core.ipynb 9
from wandb.proto import wandb_internal_pb2
from wandb.sdk.internal import datastore

# %% ../nbs/00_core.ipynb 10
def iterate_records(data_path):
    """Iterates over wandb's protobuf records in `.wandb` files."""
    # https://github.com/wandb/wandb/issues/1768#issuecomment-976786476 
    ds = datastore.DataStore()
    ds.open_for_scan(data_path)
    terminal_log = []

    data = ds.scan_record()
    while data is not None:
        pb = wandb_internal_pb2.Record()
        try:
            pb.ParseFromString(data[1])  
            yield pb
        except wandb_internal_pb2.google.protobuf.message.DecodeError:
            data = ds.scan_record()
            continue
        data = ds.scan_record()


# %% ../nbs/00_core.ipynb 11
def parse_output_log(data_path):
    """
    Parse wandb data from a given path.
    Returns the terminal log typically saved as `output.log`,
    which isn't created unless you're running in online mode.
    But, the data still exists in the `.wandb` file.
    """
    terminal_log = []
    for pb in iterate_records(data_path):
        record_type = pb.WhichOneof("record_type")
        if record_type == "output_raw":
            terminal_log.append(pb.output_raw.line)
    return "".join(terminal_log)

# %% ../nbs/00_core.ipynb 12
from collections import OrderedDict

def parse_stats(data_path):
    """
    Parse `.wandb` file to extract the system stats,
    such as CPU, GPU, memory, etc.
    """
    rows = OrderedDict()
    names = []
    for pb in iterate_records(data_path):
        if pb.stats:
            row = {}
            n = 0
            for stat in pb.stats.item:
                if stat.key not in names:
                    names.append(stat.key)
                row[stat.key] = stat.value_json
                n += 1
            if n > 0:
                rows[pb.stats.timestamp.seconds] = row
    # sort each row using names
    _rows = []
    for k, v in rows.items():
        _rows.append([k]+[v.get(name, None) for name in names])
    rows = _rows
    # build csv
    header = ['relative_seconds'] + names
    return ', '.join(header) + '\n' + '\n'.join([', '.join([str(v) for v in row]) for row in rows])

# %% ../nbs/00_core.ipynb 14
import wandb
import shutil
import os
import atexit
import time
import logging
import subprocess
import sys

from enum import IntEnum
from distutils.dir_util import copy_tree
from wandb.sdk.wandb_run import TeardownHook, TeardownStage

# don't print anything by default
logging.basicConfig(format='%(asctime)s %(message)s %(name)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

# %% ../nbs/00_core.ipynb 15
def create_dirs(run_id, user, project):
    """Create shared and local sub-directories for a run
    in the shared and local storage directories.
    Returns the Paths to the shared and local directories."""
    config = get_config()
    if len(project) == 0:
        project = "misc"
    shared_dir = Path(config['shared_storage']) / user / project / run_id
    shared_dir.mkdir(parents=True)
    local_dir = Path(config['local_storage']) / project / run_id
    local_dir.mkdir(parents=True)
    return shared_dir, local_dir

# %% ../nbs/00_core.ipynb 16
class SyncLocalCallback:
    """Callback to sync wandb dir to local storage."""
    def __init__(self):
        self.exited = False

    def register_dirs(self, local_dir, wandb_dir):
        self.local_dir = local_dir
        self.wandb_dir = wandb_dir

    def __call__(self):
        logger.info("local callback called")
        if not self.exited:
            # if dir is empty sleep
            # not clear if this is necessary
            # while len([p for p in self.wandb_dir.iterdir()]) < 1:
            #     time.sleep(1)
            #     print(f"waiting for {self.wandb_dir} to be populated")
            logger.info(f"found {len([p for p in self.wandb_dir.iterdir()])} files in {self.wandb_dir}")
            # copy wandb dir to shared dir, nothing fancy
            # copy_tree(str(self.wandb_dir), str(self.local_dir), verbose=1)
            for path_object in self.wandb_dir.rglob('*'):
                if path_object.is_file():
                    logger.info(f"copying {path_object} to {self.local_dir / path_object.relative_to(self.wandb_dir)}")
                    shutil.copy(path_object, self.local_dir / path_object.relative_to(self.wandb_dir))
                else:
                    (self.local_dir / path_object.relative_to(self.wandb_dir)).mkdir(parents=True, exist_ok=True)
            logger.info(f"copied {self.wandb_dir} to {self.local_dir}")
            self.exited = True

# %% ../nbs/00_core.ipynb 17
class SyncSharedCallback:
    """Callback to sync the shared directory with the wandb directory"""
    def __init__(self):
        self.exited = False
        self.callbacks = []

    def register_dirs(self, shared_dir, wandb_dir):
        self.shared_dir = shared_dir
        self.wandb_dir = wandb_dir

    def register_callback(self, callback):
        """
        Register functions to act as callbacks on `.wandb` files.
        That's right, my callback has callbacks.
        Expect these to return a string to save and a filename to save it as.
        """
        self.callbacks.append(callback)

    def __call__(self):
        logger.info("shared callback called")
        if not self.exited:
            # find the wandb output file:
            for path_object in self.wandb_dir.rglob('*'):
                if path_object.is_file():
                    if path_object.suffix == '.wandb':
                        wandb_file = path_object
                        break
            # parse the wandb file
            state = {'wandb_file': wandb_file}
            for callback in self.callbacks:
                s, filename = callback(state)
                # write to shared_dir
                with open(self.shared_dir / filename, 'w') as f:
                    f.write(s)
                logger.info(f"{self.shared_dir / filename} written")
            # iterate over files in wandb/files directory
            for path_object in (self.wandb_dir / 'files').rglob('*'):
                if path_object.is_file():
                    # copy file to shared_dir
                    shutil.copy(path_object, self.shared_dir)
                    logger.info(f"{path_object} copied to {self.shared_dir}")
            self.exited = True

# %% ../nbs/00_core.ipynb 18
def system_to_string(command):
    """Run system command, capture and decode the output to string."""
    if type(command) == str:
        command = command.split(' ')
    return subprocess.check_output(command).decode('utf-8')

# %% ../nbs/00_core.ipynb 19
def git_patch_callback():
    """Callback that creates a patch for the changes in the current directory."""
    return system_to_string(['git', 'diff', 'HEAD'])

# %% ../nbs/00_core.ipynb 20
def git_status():
    "Git status in currently directory"
    return system_to_string(['git', 'status'])

def git_branch():
    "Current branch"
    return system_to_string(["git", "rev-parse", "--abbrev-ref", "HEAD"])

# %% ../nbs/00_core.ipynb 21
def init(**kwargs):
    """
    A wrapper for `wandb.init`. kwargs are passed to `wandb.init` with the
    following modifications:

    - if not specified `mode` is set to `offline`
    - kwargs prefixed by "profane_" are stripped of the prefix and used to
        configure the `profane` hooks:
        - `profane_save`: a list of paths to plaintext files to save to 
        the shared directory, for example `profane_save=['README.md']`
    """
    # separate profane kwargs from wandb kwargs
    pkwargs = {}
    for k, v in kwargs.items():
        if k.startswith('profane_'):
            pkwargs[k[8:]] = v
    kwargs = {k: v for k, v in kwargs.items() if not k.startswith('profane_')}
    # initialize hooks
    local_hook = SyncLocalCallback()
    shared_hook = SyncSharedCallback()
    # initialize wandb
    if 'mode' not in kwargs: 
        kwargs['mode'] = 'offline'
    run = wandb.init(**kwargs)
    # configure hooks
    config = get_config()
    wandb_dir = Path(run.dir).parent
    username = os.environ['USER'] if 'user' not in config else config['user']
    shared_dir, local_dir = create_dirs(wandb_dir.name, username, run.project)
    shared_hook.register_dirs(shared_dir, wandb_dir)
    shared_hook.register_callback(lambda s: (parse_output_log(s['wandb_file']), 'output.log'))
    shared_hook.register_callback(lambda s: (parse_stats(s['wandb_file']), 'system_stats.csv'))
    shared_hook.register_callback(lambda s: (git_patch_callback(), 'git.patch'))
    shared_hook.register_callback(lambda s: (git_status(), 'git.status'))
    # register save paths
    if 'save' in pkwargs:
        for path in pkwargs['save']:
            if isinstance(path, str):
                path = Path(path)
            assert path.exists(), f"Path {path} does not exist"
            assert path.is_file(), f"Path {path} is not a file"
            # assuming path is plaintext
            shared_hook.register_callback(lambda s, path=path: (path.read_text(), path.name))
    shared_hook.register_callback(lambda s: (' '.join(sys.argv), 'argv.txt'))
    local_hook.register_dirs(local_dir, wandb_dir)
    # this will trigger if run.finish() is called
    def report_exit():
        print(f"profane: logs saved to {shared_dir}")
        print(f"profane: wandb copied to {local_dir}")
    run._teardown_hooks += [TeardownHook(local_hook, TeardownStage.LATE),
                            TeardownHook(shared_hook, TeardownStage.LATE),
                            TeardownHook(report_exit, TeardownStage.LATE)]
    def finish():
        logger.info("atexit profane.init finish hook called")
        run.finish()
    # this is necessary because wandb doesn't use the teardown hooks otherwise
    # so it just kind of forces it to happen
    atexit.register(finish)
    return run
