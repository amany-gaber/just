yaz@gpu:~/job_matcher$ cd api/src
yaz@gpu:~/job_matcher/api/src$ python main.py
INFO:     Will watch for changes in these directories: ['/home/yaz/job_matcher/api/src']
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [2485199] using StatReload
INFO:     Started server process [2485315]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
^CINFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [2485315]
INFO:     Stopping reloader process [2485199]
yaz@gpu:~/job_matcher/api/src$ python main.py
INFO:     Will watch for changes in these directories: ['/home/yaz/job_matcher/api/src']
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [2485892] using StatReload
INFO:     Started server process [2485956]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:58706 - "GET / HTTP/1.1" 200 OK
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 764, in app
    await self.default(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 650, in not_found
    raise HTTPException(status_code=404)
starlette.exceptions.HTTPException: 404: Not Found

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 63, in wrapped_app
    await response(scope, receive, sender)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'dict' object is not callable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/protocols/http/h11_impl.py", line 403, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/applications.py", line 112, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 182, in __call__
    await response(scope, receive, send)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'dict' object is not callable
INFO:     127.0.0.1:58710 - "GET /favicon.ico HTTP/1.1" 500 Internal Server Error
INFO:     127.0.0.1:58712 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:58712 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:58716 - "POST /voice/inference HTTP/1.1" 400 Bad Request
WARNING:  StatReload detected changes in 'routes/user.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [2485956]
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/opt/anaconda3/lib/python3.12/multiprocessing/spawn.py", line 122, in spawn_main
    exitcode = _main(fd, parent_sentinel)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/lib/python3.12/multiprocessing/spawn.py", line 131, in _main
    prepare(preparation_data)
  File "/opt/anaconda3/lib/python3.12/multiprocessing/spawn.py", line 246, in prepare
    _fixup_main_from_path(data['init_main_from_path'])
  File "/opt/anaconda3/lib/python3.12/multiprocessing/spawn.py", line 297, in _fixup_main_from_path
    main_content = runpy.run_path(main_path,
                   ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen runpy>", line 287, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "/home/yaz/job_matcher/api/src/main.py", line 3, in <module>
    from routes import router
  File "/home/yaz/job_matcher/api/src/routes/__init__.py", line 1, in <module>
    from .user import router
  File "/home/yaz/job_matcher/api/src/routes/user.py", line 2, in <module>
    from services import CVMatcher
ImportError: cannot import name 'CVMatcher' from 'services' (/home/yaz/job_matcher/api/src/services/__init__.py)
