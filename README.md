# profane

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

A hacky substitute for [sacred](https://github.com/IDSIA/sacred),
logging where, when and what experiment was run. As a comparison:

- [sacred](https://github.com/IDSIA/sacred): logs everything to MongoDB,
  requires integrating it into your code and using it to manage your
  config variables
- **profane**: logs everything to a local directory, requires no
  integration into your code, and doesn’t care about your config
  variables beyond logging them

It’s a wrapper for [weights & biases](https://github.com/wandb/wandb) so
I don’t have to write my own terminal output capture solution. It just
gets captured the same way it would be if I was looking at it in the
`wandb` dashboard. In addition, `wandb` captures various metadata that I
can just copy over, along with traces logging system metrics (which
`profane` has tools to extract to `.csv`).

This also means that the interface is the same as using `wandb`:

    from profane.core import init

    # somewhere in your script before you start your experiment:
    run = init(
        project='my_project'
    )

All kwargs are passed to `wandb` but `wandb` is run offline by default,
set `mode='online'` to change this. This runs `wandb.init` internally so
any future calls to `wandb` will work as expected.

The difference from `wandb` is that when the run finishes the logs are
copied to two locations:

- `local`: a local directory where **everything** captured gets saved;
  this is a backup of the wandb directory
- `shared`: a shared directory (I use a local git repo) where only the
  metadata and terminal logs get saved

Information about every run is saved and the logs are saved, nothing is
lost, and if I need to get more detail I can go look at the `local`
directory and find detailed information, such as all of the code if I
enable
[`settings=wandb.Settings(code_dir=".")`](https://docs.wandb.ai/guides/app/features/panels/code).

Another option to do something similar would be
[`script`](https://man7.org/linux/man-pages/man1/script.1.html) but it
would fail logging progress bars and other things that `wandb` captures
without problems. Also, it would require me to write my own solution for
capturing metadata.

## Install

I haven’t put it on pypi yet so a dev install is recommended:

``` sh
git clone git@github.com:gngdb/profane.git
cd profane
pip install -e .
```

## How to use

Before using `profane` run setup to set `local` and `shared` storage:

``` python
!profane_setup --help
```

    usage: Set up a ~/.profanerc file and register the required directories.
           [-h] [--user USER] local_storage shared_storage

    positional arguments:
      local_storage   The local storage directory, everything will be stored here.
      shared_storage  The shared storage directory, only the terminal logs and
                      metadata will be stored here.

    options:
      -h, --help      show this help message and exit
      --user USER     Optional: The user name to use for the shared storage
                      directory.

Then, as described above,
[`profane.core.init`](https://gngdb.github.io/profane/core.html#init)
can be used in place of
[`wandb.init`](https://docs.wandb.ai/ref/python/init), all `kwargs` are
passed to `wandb.init`. The only difference is the results are saved in
the directories listed above.

In addition, profane kwargs may be provided prefixed by `profane_`.
Currently, this includes:

- `profane_save` a list of paths to plaintext files that should be saved
  in the shared storage

``` python
init(
    config: Union[Dict, str, None] = None,
    project: Optional[str] = None,
    entity: Optional[str] = None,
    tags: Optional[Sequence] = None,
    group: Optional[str] = None,
    name: Optional[str] = None,
    notes: Optional[str] = None,
    profane_save: Optional[Sequence] = None,
) -> Union[Run, RunDisabled, None]
```

`project` is used to name the directory in `shared` and `local` that
will store whatever is logged.

## Example Logged

Example directory containing the metadata and logs from a run (the
`shared` dir), logged with `profane`:

``` python
from pathlib import Path

log_path = Path('./../offline-run-20230908_161004-d9b952ad')
print("- " + "\n- ".join(p.name for p in log_path.glob('*')))
```

    - requirements.txt
    - git.status
    - config.json
    - output.log
    - wandb-summary.json
    - argv.txt
    - conda-environment.yaml
    - system_stats.csv
    - wandb-metadata.json
    - git.patch

``` python
from IPython.display import Markdown, display

for file in log_path.iterdir():
    if file.is_file():
        with open(file, 'r') as f:
            contents = f.read()
        display(Markdown(f"### {file.name}"))
        display(Markdown(f"```python\n{contents}\n```"))
```

### requirements.txt

``` python
absl-py==1.4.0
appdirs==1.4.4
appnope==0.1.3
asttokens==2.2.1
attrs==23.1.0
backcall==0.2.0
backports.functools-lru-cache==1.6.4
beautifulsoup4==4.12.2
bleach==6.0.0
brotlipy==0.7.0
cachetools==5.3.1
certifi==2023.5.7
cffi==1.15.1
charset-normalizer==2.0.4
click==8.1.3
contourpy==1.0.5
cryptography==39.0.1
cycler==0.11.0
dahuffman==0.4.1
debugpy==1.5.1
decorator==5.1.1
defusedxml==0.7.1
dill==0.3.6
docker-pycreds==0.4.0
einops==0.6.1
executing==1.2.0
fastjsonschema==2.18.0
filelock==3.9.0
fonttools==4.25.0
fsspec==2023.6.0
gitdb==4.0.10
gitpython==3.1.31
gmpy2==2.1.2
google-auth-oauthlib==1.0.0
google-auth==2.21.0
grpcio==1.56.0
hjson==3.1.0
idna==3.4
importlib-metadata==6.6.0
ipykernel==6.15.0
ipython==8.14.0
jedi==0.18.2
jinja2==3.1.2
jsonschema-specifications==2023.7.1
jsonschema==4.19.0
jupyter-client==8.2.0
jupyter-core==5.3.0
jupyterlab-pygments==0.2.2
kiwisolver==1.4.4
markdown==3.4.3
markupsafe==2.1.3
matplotlib-inline==0.1.6
matplotlib==3.7.1
mistune==3.0.1
mpmath==1.2.1
munkres==1.1.4
mypy-extensions==1.0.0
nbclient==0.8.0
nbconvert==7.7.4
nbformat==5.9.2
nest-asyncio==1.5.6
networkx==2.8.4
ninja==1.11.1
numpy==1.24.3
oauthlib==3.2.2
opt-einsum==3.3.0
packaging==23.1
pandas==2.0.3
pandocfilters==1.5.0
parso==0.8.3
pathtools==0.1.2
pexpect==4.8.0
pickleshare==0.7.5
pillow==9.4.0
pip==23.0.1
platformdirs==2.5.2
profane==0.0.1
prompt-toolkit==3.0.38
protobuf==4.22.3
psutil==5.9.0
ptyprocess==0.7.0
pure-eval==0.2.2
py-cpuinfo==9.0.0
pyasn1-modules==0.3.0
pyasn1==0.5.0
pycparser==2.21
pydantic==1.10.9
pygments==2.15.1
pyopenssl==23.0.0
pyparsing==3.0.9
pyre-extensions==0.0.30
pysocks==1.7.1
python-dateutil==2.8.2
pytz==2023.3
pyyaml==6.0
pyzmq==25.1.0
referencing==0.30.2
requests-oauthlib==1.3.1
requests==2.29.0
rpds-py==0.9.2
rsa==4.9
seaborn==0.12.2
sentry-sdk==1.21.1
setproctitle==1.3.2
setuptools==66.0.0
six==1.16.0
smmap==5.0.0
soupsieve==2.4.1
stack-data==0.6.2
sympy==1.11.1
tensorboard-data-server==0.7.1
tensorboard==2.13.0
tinycss2==1.2.1
torch==2.1.0.dev20230428
torchaudio==2.1.0.dev20230428
torcheval==0.0.6
torchtnt==0.1.0
torchvision==0.16.0.dev20230428
tornado==6.2
tqdm==4.65.0
traitlets==5.9.0
typing-extensions==4.5.0
typing-inspect==0.9.0
tzdata==2023.3
urllib3==1.26.15
wandb==0.15.7
wcwidth==0.2.6
webencodings==0.5.1
werkzeug==2.3.6
wheel==0.38.4
x-transformers==1.16.9
zipp==3.15.0
```

### git.status

``` python
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
    modified:   main.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
    wandb/

no changes added to commit (use "git add" and/or "git commit -a")
```

### config.json

``` python
{
    "batch_size": 64,
    "dry_run": false,
    "epochs": 14,
    "gamma": 0.7,
    "log_interval": 10,
    "lr": 1.0,
    "no_cuda": false,
    "no_mps": false,
    "save_model": false,
    "seed": 1,
    "test_batch_size": 1000
}
```

### output.log

``` python
Train Epoch: 1 [0/60000 (0%)]   Loss: 2.300024
Train Epoch: 1 [640/60000 (1%)] Loss: 1.141236
Train Epoch: 1 [1280/60000 (2%)]    Loss: 0.711558
Train Epoch: 1 [1920/60000 (3%)]    Loss: 0.534700
Train Epoch: 1 [2560/60000 (4%)]    Loss: 0.394732
Train Epoch: 1 [3200/60000 (5%)]    Loss: 0.266415
Train Epoch: 1 [3840/60000 (6%)]    Loss: 0.233061
Train Epoch: 1 [4480/60000 (7%)]    Loss: 0.214440
Train Epoch: 1 [5120/60000 (9%)]    Loss: 0.619316
Train Epoch: 1 [5760/60000 (10%)]   Loss: 0.206452
Train Epoch: 1 [6400/60000 (11%)]   Loss: 0.418914
Train Epoch: 1 [7040/60000 (12%)]   Loss: 0.228332
Train Epoch: 1 [7680/60000 (13%)]   Loss: 0.176347
Train Epoch: 1 [8320/60000 (14%)]   Loss: 0.153546
Train Epoch: 1 [8960/60000 (15%)]   Loss: 0.230625
Train Epoch: 1 [9600/60000 (16%)]   Loss: 0.181143
Train Epoch: 1 [10240/60000 (17%)]  Loss: 0.361177
Train Epoch: 1 [10880/60000 (18%)]  Loss: 0.189232
Train Epoch: 1 [11520/60000 (19%)]  Loss: 0.392473
Train Epoch: 1 [12160/60000 (20%)]  Loss: 0.177749
Train Epoch: 1 [12800/60000 (21%)]  Loss: 0.197366
Train Epoch: 1 [13440/60000 (22%)]  Loss: 0.145951
Train Epoch: 1 [14080/60000 (23%)]  Loss: 0.208425
Train Epoch: 1 [14720/60000 (25%)]  Loss: 0.462393
Train Epoch: 1 [15360/60000 (26%)]  Loss: 0.154787
Train Epoch: 1 [16000/60000 (27%)]  Loss: 0.223398
Train Epoch: 1 [16640/60000 (28%)]  Loss: 0.088585
Train Epoch: 1 [17280/60000 (29%)]  Loss: 0.105454
Train Epoch: 1 [17920/60000 (30%)]  Loss: 0.161331
Train Epoch: 1 [18560/60000 (31%)]  Loss: 0.302365
Train Epoch: 1 [19200/60000 (32%)]  Loss: 0.151357
Train Epoch: 1 [19840/60000 (33%)]  Loss: 0.180794
Train Epoch: 1 [20480/60000 (34%)]  Loss: 0.029116
Train Epoch: 1 [21120/60000 (35%)]  Loss: 0.204436
Train Epoch: 1 [21760/60000 (36%)]  Loss: 0.048799
Train Epoch: 1 [22400/60000 (37%)]  Loss: 0.123405
Train Epoch: 1 [23040/60000 (38%)]  Loss: 0.158138
Train Epoch: 1 [23680/60000 (39%)]  Loss: 0.224575
Train Epoch: 1 [24320/60000 (41%)]  Loss: 0.062561
Train Epoch: 1 [24960/60000 (42%)]  Loss: 0.106391
Train Epoch: 1 [25600/60000 (43%)]  Loss: 0.162630
Train Epoch: 1 [26240/60000 (44%)]  Loss: 0.120360
Train Epoch: 1 [26880/60000 (45%)]  Loss: 0.299113
Train Epoch: 1 [27520/60000 (46%)]  Loss: 0.204707
Train Epoch: 1 [28160/60000 (47%)]  Loss: 0.064838
Train Epoch: 1 [28800/60000 (48%)]  Loss: 0.084399
Train Epoch: 1 [29440/60000 (49%)]  Loss: 0.068435
Train Epoch: 1 [30080/60000 (50%)]  Loss: 0.054200
Train Epoch: 1 [30720/60000 (51%)]  Loss: 0.083719
Train Epoch: 1 [31360/60000 (52%)]  Loss: 0.057806
Train Epoch: 1 [32000/60000 (53%)]  Loss: 0.168371
Train Epoch: 1 [32640/60000 (54%)]  Loss: 0.103747
Train Epoch: 1 [33280/60000 (55%)]  Loss: 0.143636
Train Epoch: 1 [33920/60000 (57%)]  Loss: 0.073810
Train Epoch: 1 [34560/60000 (58%)]  Loss: 0.071079
Train Epoch: 1 [35200/60000 (59%)]  Loss: 0.096664
Train Epoch: 1 [35840/60000 (60%)]  Loss: 0.180809
Train Epoch: 1 [36480/60000 (61%)]  Loss: 0.078782
Train Epoch: 1 [37120/60000 (62%)]  Loss: 0.085670
Train Epoch: 1 [37760/60000 (63%)]  Loss: 0.237285
Train Epoch: 1 [38400/60000 (64%)]  Loss: 0.171452
Train Epoch: 1 [39040/60000 (65%)]  Loss: 0.016421
Train Epoch: 1 [39680/60000 (66%)]  Loss: 0.039804
Train Epoch: 1 [40320/60000 (67%)]  Loss: 0.123339
Train Epoch: 1 [40960/60000 (68%)]  Loss: 0.179846
Train Epoch: 1 [41600/60000 (69%)]  Loss: 0.050442
Train Epoch: 1 [42240/60000 (70%)]  Loss: 0.017428
Train Epoch: 1 [42880/60000 (71%)]  Loss: 0.173062
Train Epoch: 1 [43520/60000 (72%)]  Loss: 0.182993
Train Epoch: 1 [44160/60000 (74%)]  Loss: 0.013076
Train Epoch: 1 [44800/60000 (75%)]  Loss: 0.178473
Train Epoch: 1 [45440/60000 (76%)]  Loss: 0.167469
Train Epoch: 1 [46080/60000 (77%)]  Loss: 0.169292
Train Epoch: 1 [46720/60000 (78%)]  Loss: 0.224109
Train Epoch: 1 [47360/60000 (79%)]  Loss: 0.088818
Train Epoch: 1 [48000/60000 (80%)]  Loss: 0.144786
Train Epoch: 1 [48640/60000 (81%)]  Loss: 0.038873
Train Epoch: 1 [49280/60000 (82%)]  Loss: 0.030595
Train Epoch: 1 [49920/60000 (83%)]  Loss: 0.070011
Train Epoch: 1 [50560/60000 (84%)]  Loss: 0.124998
Train Epoch: 1 [51200/60000 (85%)]  Loss: 0.224721
Train Epoch: 1 [51840/60000 (86%)]  Loss: 0.066481
Train Epoch: 1 [52480/60000 (87%)]  Loss: 0.028962
Train Epoch: 1 [53120/60000 (88%)]  Loss: 0.203254
Train Epoch: 1 [53760/60000 (90%)]  Loss: 0.151286
Train Epoch: 1 [54400/60000 (91%)]  Loss: 0.035127
Train Epoch: 1 [55040/60000 (92%)]  Loss: 0.032851
Train Epoch: 1 [55680/60000 (93%)]  Loss: 0.188284
Train Epoch: 1 [56320/60000 (94%)]  Loss: 0.036238
Train Epoch: 1 [56960/60000 (95%)]  Loss: 0.046339
Train Epoch: 1 [57600/60000 (96%)]  Loss: 0.106009
Train Epoch: 1 [58240/60000 (97%)]  Loss: 0.072917
Train Epoch: 1 [58880/60000 (98%)]  Loss: 0.001254
Train Epoch: 1 [59520/60000 (99%)]  Loss: 0.013900

Test set: Average loss: 0.0484, Accuracy: 9838/10000 (98%)

Train Epoch: 2 [0/60000 (0%)]   Loss: 0.060924
Train Epoch: 2 [640/60000 (1%)] Loss: 0.057691
Train Epoch: 2 [1280/60000 (2%)]    Loss: 0.056489
Train Epoch: 2 [1920/60000 (3%)]    Loss: 0.083914
Train Epoch: 2 [2560/60000 (4%)]    Loss: 0.086739
Train Epoch: 2 [3200/60000 (5%)]    Loss: 0.029744
Train Epoch: 2 [3840/60000 (6%)]    Loss: 0.035730
Traceback (most recent call last):
  File "/Users/gngdb/ws/pytorch_examples/mnist/main.py", line 149, in <module>
    main()
  File "/Users/gngdb/ws/pytorch_examples/mnist/main.py", line 140, in main
    train(args, model, device, train_loader, optimizer, epoch)
  File "/Users/gngdb/ws/pytorch_examples/mnist/main.py", line 45, in train
    optimizer.step()
  File "/opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly/lib/python3.11/site-packages/torch/optim/lr_scheduler.py", line 69, in wrapper
    return wrapped(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly/lib/python3.11/site-packages/torch/optim/optimizer.py", line 280, in wrapper
    out = func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly/lib/python3.11/site-packages/torch/optim/optimizer.py", line 33, in _use_grad
    ret = func(self, *args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly/lib/python3.11/site-packages/torch/optim/adadelta.py", line 108, in step
    adadelta(
  File "/opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly/lib/python3.11/site-packages/torch/optim/adadelta.py", line 206, in adadelta
    func(
  File "/opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly/lib/python3.11/site-packages/torch/optim/adadelta.py", line 253, in _single_tensor_adadelta
    acc_delta.mul_(rho).addcmul_(delta, delta, value=1 - rho)
KeyboardInterrupt
```

### wandb-summary.json

``` python
{"_wandb": {"runtime": 13}}
```

### argv.txt

``` python
main.py
```

### conda-environment.yaml

``` python
name: torch_nightly
channels:
  - pytorch-nightly
  - conda-forge
  - defaults
dependencies:
  - appnope=0.1.3=pyhd8ed1ab_0
  - asttokens=2.2.1=pyhd8ed1ab_0
  - backcall=0.2.0=pyh9f0ad1d_0
  - backports=1.0=pyhd8ed1ab_3
  - backports.functools_lru_cache=1.6.4=pyhd8ed1ab_0
  - blas=1.0=openblas
  - brotli=1.0.9=h1a28f6b_7
  - brotli-bin=1.0.9=h1a28f6b_7
  - brotlipy=0.7.0=py311h80987f9_1002
  - bzip2=1.0.8=h620ffc9_4
  - ca-certificates=2023.05.30=hca03da5_0
  - certifi=2023.5.7=py311hca03da5_0
  - cffi=1.15.1=py311h80987f9_3
  - charset-normalizer=2.0.4=pyhd3eb1b0_0
  - contourpy=1.0.5=py311h48ca7d4_0
  - cryptography=39.0.1=py311h834c97f_0
  - cycler=0.11.0=pyhd3eb1b0_0
  - debugpy=1.5.1=py311h313beb8_0
  - decorator=5.1.1=pyhd8ed1ab_0
  - executing=1.2.0=pyhd8ed1ab_0
  - ffmpeg=4.2.2=h04105a8_0
  - filelock=3.9.0=py311hca03da5_0
  - fonttools=4.25.0=pyhd3eb1b0_0
  - freetype=2.12.1=h1192e45_0
  - gettext=0.21.0=h13f89a0_1
  - giflib=5.2.1=h80987f9_3
  - gmp=6.2.1=hc377ac9_3
  - gmpy2=2.1.2=py311h40f64dc_0
  - gnutls=3.6.15=h887c41c_0
  - icu=68.1=hc377ac9_0
  - idna=3.4=py311hca03da5_0
  - importlib-metadata=6.6.0=pyha770c72_0
  - importlib_metadata=6.6.0=hd8ed1ab_0
  - ipykernel=6.15.0=pyh736e0ef_0
  - ipython=8.14.0=pyhd1c38e8_0
  - jedi=0.18.2=pyhd8ed1ab_0
  - jpeg=9e=h80987f9_1
  - jupyter_client=8.2.0=pyhd8ed1ab_0
  - jupyter_core=5.3.0=py311hca03da5_0
  - kiwisolver=1.4.4=py311h313beb8_0
  - lame=3.100=h1a28f6b_0
  - lcms2=2.12=hba8e193_0
  - lerc=3.0=hc377ac9_0
  - libbrotlicommon=1.0.9=h1a28f6b_7
  - libbrotlidec=1.0.9=h1a28f6b_7
  - libbrotlienc=1.0.9=h1a28f6b_7
  - libcxx=14.0.6=h848a8c0_0
  - libdeflate=1.17=h80987f9_0
  - libffi=3.4.2=hca03da5_6
  - libgfortran=5.0.0=11_3_0_hca03da5_28
  - libgfortran5=11.3.0=h009349e_28
  - libiconv=1.16=h1a28f6b_2
  - libidn2=2.3.1=h1a28f6b_0
  - libopenblas=0.3.21=h269037a_0
  - libopus=1.3=h1a28f6b_1
  - libpng=1.6.39=h80987f9_0
  - libsodium=1.0.18=h27ca646_1
  - libtasn1=4.19.0=h80987f9_0
  - libtiff=4.5.0=h313beb8_2
  - libunistring=0.9.10=h1a28f6b_0
  - libvpx=1.10.0=hc377ac9_0
  - libwebp=1.2.4=ha3663a8_1
  - libwebp-base=1.2.4=h80987f9_1
  - libxml2=2.10.3=h372ba2a_0
  - llvm-openmp=14.0.6=hc6e5704_0
  - lz4-c=1.9.4=h313beb8_0
  - matplotlib=3.7.1=py311hca03da5_1
  - matplotlib-base=3.7.1=py311h7aedaa7_1
  - matplotlib-inline=0.1.6=pyhd8ed1ab_0
  - mpc=1.1.0=h8c48613_1
  - mpfr=4.0.2=h695f6f0_1
  - mpmath=1.2.1=py311hca03da5_0
  - munkres=1.1.4=py_0
  - ncurses=6.4=h313beb8_0
  - nest-asyncio=1.5.6=pyhd8ed1ab_0
  - nettle=3.7.3=h84b5d62_1
  - networkx=2.8.4=py311hca03da5_1
  - numpy=1.24.3=py311hb57d4eb_0
  - numpy-base=1.24.3=py311h1d85a46_0
  - openh264=1.8.0=h98b2900_0
  - openssl=1.1.1u=h1a28f6b_0
  - packaging=23.1=pyhd8ed1ab_0
  - parso=0.8.3=pyhd8ed1ab_0
  - pexpect=4.8.0=pyh1a96a4e_2
  - pickleshare=0.7.5=py_1003
  - pillow=9.4.0=py311h313beb8_0
  - pip=23.0.1=py311hca03da5_0
  - platformdirs=2.5.2=py311hca03da5_0
  - prompt-toolkit=3.0.38=pyha770c72_0
  - prompt_toolkit=3.0.38=hd8ed1ab_0
  - ptyprocess=0.7.0=pyhd3deb0d_0
  - pure_eval=0.2.2=pyhd8ed1ab_0
  - pycparser=2.21=pyhd3eb1b0_0
  - pygments=2.15.1=pyhd8ed1ab_0
  - pyopenssl=23.0.0=py311hca03da5_0
  - pyparsing=3.0.9=py311hca03da5_0
  - pysocks=1.7.1=py311hca03da5_0
  - python=3.11.3=hc0d8a6c_0
  - python-dateutil=2.8.2=pyhd8ed1ab_0
  - pytorch=2.1.0.dev20230428=py3.11_0
  - pyzmq=25.1.0=py311h313beb8_0
  - readline=8.2=h1a28f6b_0
  - requests=2.29.0=py311hca03da5_0
  - setuptools=66.0.0=py311hca03da5_0
  - six=1.16.0=pyh6c4a22f_0
  - sqlite=3.41.2=h80987f9_0
  - stack_data=0.6.2=pyhd8ed1ab_0
  - sympy=1.11.1=py311hca03da5_0
  - tk=8.6.12=hb8d0fd4_0
  - torchaudio=2.1.0.dev20230428=py311_cpu
  - torchvision=0.16.0.dev20230428=py311_cpu
  - tornado=6.2=py311h80987f9_0
  - traitlets=5.9.0=pyhd8ed1ab_0
  - typing_extensions=4.5.0=py311hca03da5_0
  - urllib3=1.26.15=py311hca03da5_0
  - wcwidth=0.2.6=pyhd8ed1ab_0
  - wheel=0.38.4=py311hca03da5_0
  - x264=1!152.20180806=h1a28f6b_0
  - xz=5.2.10=h80987f9_1
  - zeromq=4.3.4=hbdafb3b_1
  - zipp=3.15.0=pyhd8ed1ab_0
  - zlib=1.2.13=h5a0b063_0
  - zstd=1.5.5=hd90d995_0
  - pip:
      - absl-py==1.4.0
      - appdirs==1.4.4
      - attrs==23.1.0
      - beautifulsoup4==4.12.2
      - bleach==6.0.0
      - cachetools==5.3.1
      - click==8.1.3
      - dahuffman==0.4.1
      - defusedxml==0.7.1
      - dill==0.3.6
      - docker-pycreds==0.4.0
      - einops==0.6.1
      - fastjsonschema==2.18.0
      - fsspec==2023.6.0
      - gitdb==4.0.10
      - gitpython==3.1.31
      - google-auth==2.21.0
      - google-auth-oauthlib==1.0.0
      - grpcio==1.56.0
      - hjson==3.1.0
      - jinja2==3.1.2
      - jsonschema==4.19.0
      - jsonschema-specifications==2023.7.1
      - jupyterlab-pygments==0.2.2
      - markdown==3.4.3
      - markupsafe==2.1.3
      - mistune==3.0.1
      - mypy-extensions==1.0.0
      - nbclient==0.8.0
      - nbconvert==7.7.4
      - nbformat==5.9.2
      - ninja==1.11.1
      - oauthlib==3.2.2
      - opt-einsum==3.3.0
      - pandas==2.0.3
      - pandocfilters==1.5.0
      - pathtools==0.1.2
      - protobuf==4.22.3
      - psutil==5.9.5
      - py-cpuinfo==9.0.0
      - pyasn1==0.5.0
      - pyasn1-modules==0.3.0
      - pydantic==1.10.9
      - pyre-extensions==0.0.30
      - pytz==2023.3
      - pyyaml==6.0
      - referencing==0.30.2
      - requests-oauthlib==1.3.1
      - rpds-py==0.9.2
      - rsa==4.9
      - seaborn==0.12.2
      - sentry-sdk==1.21.1
      - setproctitle==1.3.2
      - smmap==5.0.0
      - soupsieve==2.4.1
      - tensorboard==2.13.0
      - tensorboard-data-server==0.7.1
      - tinycss2==1.2.1
      - torcheval==0.0.6
      - torchtnt==0.1.0
      - tqdm==4.65.0
      - typing-inspect==0.9.0
      - tzdata==2023.3
      - wandb==0.15.7
      - webencodings==0.5.1
      - werkzeug==2.3.6
      - x-transformers==1.16.9
prefix: /opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly
```

### system_stats.csv

``` python
relative_seconds, gpu.0.gpu, gpu.0.memoryAllocated, gpu.0.temp, gpu.0.powerWatts, gpu.0.powerPercent, proc.memory.availableMB, memory, proc.memory.rssMB, proc.memory.percent, cpu, cpu.0.cpu_percent, cpu.1.cpu_percent, cpu.2.cpu_percent, cpu.3.cpu_percent, cpu.4.cpu_percent, cpu.5.cpu_percent, cpu.6.cpu_percent, cpu.7.cpu_percent, cpu.8.cpu_percent, cpu.9.cpu_percent, proc.cpu.threads, network.sent, network.recv, disk
0, 74.6, 31.54, 34.14, 6.37, 38.63, 3455.99, 78.9, 386.97, 2.36, 7.22, 29.36, 28.97, 55.53, 31.24, 13.1, 9.1, 5.21, 1.36, 0.71, 0.5, 15, 27940.57, 164717.71, 9.3
```

### wandb-metadata.json

``` python
{
    "os": "macOS-13.5.1-arm64-arm-64bit",
    "python": "3.11.3",
    "heartbeatAt": "2023-09-08T20:10:04.564308",
    "startedAt": "2023-09-08T20:10:04.524040",
    "docker": null,
    "cuda": null,
    "args": [],
    "state": "running",
    "program": "/Users/gngdb/ws/pytorch_examples/mnist/main.py",
    "codePath": "mnist/main.py",
    "git": {
        "remote": "git@github.com:pytorch/examples.git",
        "commit": "cead596caa90600188e1055cd9166ab4e7dfd303"
    },
    "email": "***REMOVED***",
    "root": "/Users/gngdb/ws/pytorch_examples",
    "host": "Gavias-MacBook-Pro.local",
    "username": "gngdb",
    "executable": "/opt/homebrew/Caskroom/miniconda/base/envs/torch_nightly/bin/python",
    "cpu_count": 10,
    "cpu_count_logical": 10,
    "disk": {
        "total": 926.3517189025879,
        "used": 86.2264518737793
    },
    "gpuapple": {
        "type": "arm",
        "vendor": "Apple"
    },
    "memory": {
        "total": 16.0
    }
}
```

### git.patch

``` python
diff --git a/mnist/main.py b/mnist/main.py
index 29d81d6..a95afa2 100644
--- a/mnist/main.py
+++ b/mnist/main.py
@@ -99,6 +99,10 @@ def main():
     use_cuda = not args.no_cuda and torch.cuda.is_available()
     use_mps = not args.no_mps and torch.backends.mps.is_available()
 
+    from profane.core import init
+
+    init(config=vars(args), project='mnist')
+
     torch.manual_seed(args.seed)
 
     if use_cuda:
```
