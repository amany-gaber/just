the frist on api/src
1- python services/main.py
2- cd ..
3- make bulid
4-uvicorn main:main --host 0.0.0.0 --port 8000
5-docker ps  to take image name
6- docker image name logs
7-docker run -d -p 4444:4444 --name emotion-api emotion-inference-api
8-docker build -t emotion-inference-api . if you chane in docker file or req file
9-docker rm -f emotion-api
