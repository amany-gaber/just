api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-91:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-92:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2233]
api-1  | INFO:     Child process [2233] died
api-1  | INFO:     Waiting for child process [2259]
api-1  | INFO:     Child process [2259] died
api-1  | INFO:     Waiting for child process [2258]
api-1  | INFO:     Child process [2258] died
api-1  | Process SpawnProcess-93:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-94:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2308]
api-1  | INFO:     Child process [2308] died
api-1  | INFO:     Waiting for child process [2309]
api-1  | INFO:     Child process [2309] died
api-1  | Process SpawnProcess-95:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2358]
api-1  | INFO:     Child process [2358] died
api-1  | Process SpawnProcess-96:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-97:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2383]
api-1  | INFO:     Child process [2383] died
api-1  | INFO:     Waiting for child process [2384]
api-1  | INFO:     Child process [2384] died
api-1  | Process SpawnProcess-98:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2433]
api-1  | INFO:     Child process [2433] died
api-1  | Process SpawnProcess-100:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-99:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-101:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2458]
api-1  | INFO:     Child process [2458] died
api-1  | INFO:     Waiting for child process [2459]
api-1  | INFO:     Child process [2459] died
api-1  | INFO:     Waiting for child process [2508]
api-1  | INFO:     Child process [2508] died
api-1  | Process SpawnProcess-102:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-103:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2533]
api-1  | INFO:     Child process [2533] died
api-1  | Process SpawnProcess-104:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-105:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2534]
api-1  | INFO:     Child process [2534] died
api-1  | INFO:     Waiting for child process [2583]
api-1  | INFO:     Child process [2583] died
api-1  | INFO:     Waiting for child process [2608]
api-1  | INFO:     Child process [2608] died
api-1  | Process SpawnProcess-106:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2633]
api-1  | INFO:     Child process [2633] died
api-1  | Process SpawnProcess-107:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-108:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2658]
api-1  | INFO:     Child process [2658] died
api-1  | Process SpawnProcess-109:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-110:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | INFO:     Waiting for child process [2659]
api-1  | INFO:     Child process [2659] died
api-1  | INFO:     Waiting for child process [2708]
api-1  | INFO:     Child process [2708] died
api-1  | INFO:     Waiting for child process [2733]
api-1  | INFO:     Child process [2733] died
api-1  | Process SpawnProcess-112:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-111:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
api-1  | Process SpawnProcess-113:
api-1  | Traceback (most recent call last):
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
api-1  |     self.run()
api-1  |   File "/usr/local/lib/python3.9/multiprocessing/process.py", line 108, in run
api-1  |     self._target(*self._args, **self._kwargs)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
api-1  |     target(sockets=sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/supervisors/multiprocess.py", line 63, in target
api-1  |     return self.real_target(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 65, in run
api-1  |     return asyncio.run(self.serve(sockets=sockets))
api-1  |   File "/usr/local/lib/python3.9/asyncio/runners.py", line 44, in run
api-1  |     return loop.run_until_complete(main)
api-1  |   File "/usr/local/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
api-1  |     return future.result()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 69, in serve
api-1  |     await self._serve(sockets)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/server.py", line 76, in _serve
api-1  |     config.load()
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/config.py", line 434, in load
api-1  |     self.loaded_app = import_from_string(self.app)
api-1  |   File "/usr/local/lib/python3.9/site-packages/uvicorn/importer.py", line 19, in import_from_string
api-1  |     module = importlib.import_module(module_str)
api-1  |   File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
api-1  |     return _bootstrap._gcd_import(name[level:], package, level)
api-1  |   File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
api-1  |   File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
api-1  |   File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
api-1  |   File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
api-1  |   File "<frozen importlib._bootstrap_external>", line 850, in exec_module
api-1  |   File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
api-1  |   File "/home/docker/app/main.py", line 3, in <module>
api-1  |     from routes.user import router
api-1  |   File "/home/docker/app/routes/__init__.py", line 3, in <module>
api-1  |     from .user import router
api-1  |   File "/home/docker/app/routes/user.py", line 10, in <module>
api-1  |     job_matcher = JobMatcher()
api-1  |   File "/home/docker/app/services/main.py", line 29, in __init__
api-1  |     raise ValueError(self.error)
api-1  | ValueError: File not found: /home/yaz/specific_job/api/src/static/job_data.csv
Gracefully stopping... (press Ctrl+C again to force)
[+] Stopping 1/1
 ✔ Container spisficjob-api-1  Stopped                                                                                                                                  5.4s 
yaz@gpu:~/specific_job$ 
