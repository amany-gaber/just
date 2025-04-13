yaz is not in the sudoers file.
(newnev) yaz@gpu:~/Voice-toon$ pip install librosa
Collecting librosa
  Downloading librosa-0.11.0-py3-none-any.whl.metadata (8.7 kB)
Collecting audioread>=2.1.9 (from librosa)
  Downloading audioread-3.0.1-py3-none-any.whl.metadata (8.4 kB)
Collecting numba>=0.51.0 (from librosa)
  Downloading numba-0.61.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.8 kB)
Requirement already satisfied: numpy>=1.22.3 in ./newnev/lib/python3.12/site-packages (from librosa) (1.26.4)
Requirement already satisfied: scipy>=1.6.0 in ./newnev/lib/python3.12/site-packages (from librosa) (1.15.2)
Requirement already satisfied: scikit-learn>=1.1.0 in ./newnev/lib/python3.12/site-packages (from librosa) (1.6.1)
Requirement already satisfied: joblib>=1.0 in ./newnev/lib/python3.12/site-packages (from librosa) (1.4.2)
Collecting decorator>=4.3.0 (from librosa)
  Downloading decorator-5.2.1-py3-none-any.whl.metadata (3.9 kB)
Requirement already satisfied: soundfile>=0.12.1 in ./newnev/lib/python3.12/site-packages (from librosa) (0.13.1)
Collecting pooch>=1.1 (from librosa)
  Downloading pooch-1.8.2-py3-none-any.whl.metadata (10 kB)
Collecting soxr>=0.3.2 (from librosa)
  Downloading soxr-0.5.0.post1-cp312-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (5.6 kB)
Requirement already satisfied: typing_extensions>=4.1.1 in ./newnev/lib/python3.12/site-packages (from librosa) (4.12.2)
Collecting lazy_loader>=0.1 (from librosa)
  Downloading lazy_loader-0.4-py3-none-any.whl.metadata (7.6 kB)
Collecting msgpack>=1.0 (from librosa)
  Downloading msgpack-1.1.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (8.4 kB)
Requirement already satisfied: packaging in ./newnev/lib/python3.12/site-packages (from lazy_loader>=0.1->librosa) (24.2)
Collecting llvmlite<0.45,>=0.44.0dev0 (from numba>=0.51.0->librosa)
  Downloading llvmlite-0.44.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (5.0 kB)
Collecting platformdirs>=2.5.0 (from pooch>=1.1->librosa)
  Downloading platformdirs-4.3.7-py3-none-any.whl.metadata (11 kB)
Requirement already satisfied: requests>=2.19.0 in ./newnev/lib/python3.12/site-packages (from pooch>=1.1->librosa) (2.32.3)
Requirement already satisfied: threadpoolctl>=3.1.0 in ./newnev/lib/python3.12/site-packages (from scikit-learn>=1.1.0->librosa) (3.6.0)
Requirement already satisfied: cffi>=1.0 in ./newnev/lib/python3.12/site-packages (from soundfile>=0.12.1->librosa) (1.17.1)
Requirement already satisfied: pycparser in ./newnev/lib/python3.12/site-packages (from cffi>=1.0->soundfile>=0.12.1->librosa) (2.22)
Requirement already satisfied: charset-normalizer<4,>=2 in ./newnev/lib/python3.12/site-packages (from requests>=2.19.0->pooch>=1.1->librosa) (3.4.1)
Requirement already satisfied: idna<4,>=2.5 in ./newnev/lib/python3.12/site-packages (from requests>=2.19.0->pooch>=1.1->librosa) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in ./newnev/lib/python3.12/site-packages (from requests>=2.19.0->pooch>=1.1->librosa) (2.3.0)
Requirement already satisfied: certifi>=2017.4.17 in ./newnev/lib/python3.12/site-packages (from requests>=2.19.0->pooch>=1.1->librosa) (2025.1.31)
Downloading librosa-0.11.0-py3-none-any.whl (260 kB)
Downloading audioread-3.0.1-py3-none-any.whl (23 kB)
Downloading decorator-5.2.1-py3-none-any.whl (9.2 kB)
Downloading lazy_loader-0.4-py3-none-any.whl (12 kB)
Downloading msgpack-1.1.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (401 kB)
Downloading numba-0.61.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (3.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.9/3.9 MB 2.2 MB/s eta 0:00:00
Downloading pooch-1.8.2-py3-none-any.whl (64 kB)
Downloading soxr-0.5.0.post1-cp312-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (248 kB)
Downloading llvmlite-0.44.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (42.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 42.4/42.4 MB 2.3 MB/s eta 0:00:00
Downloading platformdirs-4.3.7-py3-none-any.whl (18 kB)
Installing collected packages: soxr, platformdirs, msgpack, llvmlite, lazy_loader, decorator, audioread, pooch, numba, librosa
Successfully installed audioread-3.0.1 decorator-5.2.1 lazy_loader-0.4 librosa-0.11.0 llvmlite-0.44.0 msgpack-1.1.0 numba-0.61.2 platformdirs-4.3.7 pooch-1.8.2 soxr-0.5.0.post1

[notice] A new release of pip is available: 24.2 -> 25.0.1
[notice] To update, run: pip install --upgrade pip
(newnev) yaz@gpu:~/Voice-toon$ ip install --upgrade pip
Object "install" is unknown, try "ip help".
(newnev) yaz@gpu:~/Voice-toon$ pip install --upgrade pip
Requirement already satisfied: pip in ./newnev/lib/python3.12/site-packages (24.2)
Collecting pip
  Downloading pip-25.0.1-py3-none-any.whl.metadata (3.7 kB)
Downloading pip-25.0.1-py3-none-any.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 452.1 kB/s eta 0:00:00
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 24.2
    Uninstalling pip-24.2:
      Successfully uninstalled pip-24.2
Successfully installed pip-25.0.1
(newnev) yaz@gpu:~/Voice-toon$ cd api/src
(newnev) yaz@gpu:~/Voice-toon/api/src$ python services/main.py
(newnev) yaz@gpu:~/Voice-toon/api/src$ uvicorn app:app --reload --port 8000
INFO:     Will watch for changes in these directories: ['/home/yaz/Voice-toon/api/src']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [2834808] using StatReload
ERROR:    Error loading ASGI app. Could not import module "app".
uvicorn app:app --reload --port 8000
^CINFO:     Stopping reloader process [2834808]
(newnev) yaz@gpu:~/Voice-toon/api/src$ uvicorn main:app --reload --port 8000
INFO:     Will watch for changes in these directories: ['/home/yaz/Voice-toon/api/src']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [2835491] using StatReload
Process SpawnProcess-1:
Traceback (most recent call last):
  File "/opt/anaconda3/lib/python3.12/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/opt/anaconda3/lib/python3.12/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/yaz/Voice-toon/newnev/lib/python3.12/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
  File "/home/yaz/Voice-toon/newnev/lib/python3.12/site-packages/uvicorn/server.py", line 66, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/yaz/Voice-toon/newnev/lib/python3.12/site-packages/uvicorn/server.py", line 70, in serve
    await self._serve(sockets)
  File "/home/yaz/Voice-toon/newnev/lib/python3.12/site-packages/uvicorn/server.py", line 77, in _serve
    config.load()
  File "/home/yaz/Voice-toon/newnev/lib/python3.12/site-packages/uvicorn/config.py", line 435, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/yaz/Voice-toon/newnev/lib/python3.12/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/home/yaz/Voice-toon/api/src/main.py", line 3, in <module>
    from routes import router
  File "/home/yaz/Voice-toon/api/src/routes/__init__.py", line 1, in <module>
    from .user import router
  File "/home/yaz/Voice-toon/api/src/routes/user.py", line 15, in <module>
    model_inference = EmotionInference()
                      ^^^^^^^^^^^^^^^^^^
  File "/home/yaz/Voice-toon/api/src/services/main.py", line 16, in __init__
    raise FileNotFoundError(f"Model not found at: {self.model_path}")
FileNotFoundError: Model not found at: /home/docker/app/static/wav2vec2_emotion.onnx
