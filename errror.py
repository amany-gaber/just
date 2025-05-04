.1.0 in /opt/anaconda3/lib/python3.12/site-packages (from python-docx->-r requirements.txt (line 12)) (5.2.1)
Requirement already satisfied: scipy>=1.6.0 in /opt/anaconda3/lib/python3.12/site-packages (from scikit-learn->-r requirements.txt (line 14)) (1.13.1)
Requirement already satisfied: joblib>=1.2.0 in /opt/anaconda3/lib/python3.12/site-packages (from scikit-learn->-r requirements.txt (line 14)) (1.4.2)
Requirement already satisfied: threadpoolctl>=3.1.0 in /opt/anaconda3/lib/python3.12/site-packages (from scikit-learn->-r requirements.txt (line 14)) (3.5.0)
Requirement already satisfied: six>=1.5 in /opt/anaconda3/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas->-r requirements.txt (line 11)) (1.16.0)
Requirement already satisfied: anyio<5,>=3.6.2 in /opt/anaconda3/lib/python3.12/site-packages (from starlette<0.47.0,>=0.40.0->fastapi->-r requirements.txt (line 3)) (4.2.0)
Requirement already satisfied: idna>=2.8 in /opt/anaconda3/lib/python3.12/site-packages (from anyio<5,>=3.6.2->starlette<0.47.0,>=0.40.0->fastapi->-r requirements.txt (line 3)) (3.7)
Requirement already satisfied: sniffio>=1.1 in /opt/anaconda3/lib/python3.12/site-packages (from anyio<5,>=3.6.2->starlette<0.47.0,>=0.40.0->fastapi->-r requirements.txt (line 3)) (1.3.0)
Downloading python_docx-1.1.2-py3-none-any.whl (244 kB)
Downloading pypdf2-3.0.1-py3-none-any.whl (232 kB)
Installing collected packages: python-docx, PyPDF2
Successfully installed PyPDF2-3.0.1 python-docx-1.1.2
yaz@gpu:~/job_matcher/api$ cd src
yaz@gpu:~/job_matcher/api/src$ python main.py
INFO:     Will watch for changes in these directories: ['/home/yaz/job_matcher/api/src']
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [2514146] using StatReload
INFO:     Started server process [2514169]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:46142 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:46142 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:59506 - "POST /cv/inference HTTP/1.1" 500 Internal Server Error
INFO:     127.0.0.1:40936 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:40936 - "GET /openapi.json HTTP/1.1" 200 OK

 *  History restored 

yaz@gpu:~/job_matcher/api/src$ python main.py
INFO:     Will watch for changes in these directories: ['/home/yaz/job_matcher/api/src']
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [2524588] using StatReload
INFO:     Started server process [2524600]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:34600 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:34600 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:48504 - "POST /cv/inference HTTP/1.1" 500 Internal Server Error
INFO:     127.0.0.1:39856 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:39856 - "GET /openapi.json HTTP/1.1" 200 OK
^CINFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [2524600]
INFO:     Stopping reloader process [2524588]
yaz@gpu:~/job_matcher/api/src$ python main.py
INFO:     Will watch for changes in these directories: ['/home/yaz/job_matcher/api/src']
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [2526694] using StatReload
INFO:     Started server process [2526718]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
WARNING:  StatReload detected changes in 'schemas/user.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [2526718]
INFO:     Started server process [2529714]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

 *  History restored 

yaz@gpu:~/job_matcher/api/src$ python main.py
INFO:     Will watch for changes in these directories: ['/home/yaz/job_matcher/api/src']
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [2675248] using StatReload
INFO:     Started server process [2675271]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:56526 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:56526 - "GET /openapi.json HTTP/1.1" 200 OK
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/home/yaz/.local/lib/python3.12/site-packages/fastapi/encoders.py", line 324, in jsonable_encoder
    data = dict(obj)
           ^^^^^^^^^
TypeError: 'coroutine' object is not iterable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/yaz/.local/lib/python3.12/site-packages/fastapi/encoders.py", line 329, in jsonable_encoder
    data = vars(obj)
           ^^^^^^^^^
TypeError: vars() argument must have __dict__ attribute

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 93, in __call__
    await self.simple_response(scope, receive, send, request_headers=headers)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 144, in simple_response
    await self.app(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/home/yaz/.local/lib/python3.12/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/fastapi/routing.py", line 327, in app
    content = await serialize_response(
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/fastapi/routing.py", line 201, in serialize_response
    return jsonable_encoder(response_content)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/yaz/.local/lib/python3.12/site-packages/fastapi/encoders.py", line 332, in jsonable_encoder
    raise ValueError(errors) from e
ValueError: [TypeError("'coroutine' object is not iterable"), TypeError('vars() argument must have __dict__ attribute')]

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
INFO:     127.0.0.1:45078 - "POST /cv/inference HTTP/1.1" 500 Internal Server Error
