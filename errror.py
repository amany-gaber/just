yaz@gpu:~/specific_job/api/src$ python main.py
Traceback (most recent call last):
  File "/home/yaz/specific_job/api/src/main.py", line 3, in <module>
    from src.routes.user import router
ModuleNotFoundError: No module named 'src'
yaz@gpu:~/specific_job/api/src$ python main.py
Traceback (most recent call last):
  File "/home/yaz/specific_job/api/src/main.py", line 3, in <module>
    from .routes.user import router
