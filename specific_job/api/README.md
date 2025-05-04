# API Details

This template doesn't contain Database

## API Structure

```bash

├── src                         # directory for source code for the whole API logic 
│    ├── config                 # dir for app configuration
│    │   └── setting.py         # file that contain app settings (APP_ROOT, APP_NAME, ...)
│    │
│    ├── schemas                # dir for app schemas
│    │   └── user.py            # file that contain users schemas (can be multi-file for multi-user type)
│    ├── routes                 # dir for routes and init for fastAPI
│    │   ├── service.py         # file that contain services endpoints (can be multi-file for multi-service)
│    │   └── user.py            # file that contain users endpoints (can be multi-file for multi-user type)
│    ├── services               # dir to store main services
│    │   ├── service1           # 
│    │   ├── service2           # 
│    │   └── ...                # 
│    ├── static                 # dir to store project assests (Optional)
│    │   ├── models             # dir to store models (Optional)
│    │   └── runs               # dir to store temp files while runing (Optional)
│    │
│    └── main.py                # runner file : to start the server using it.
├── venv                        # directory for virtual env, It's required for docker compose 
├── Dockerfile                  # docker file for production
├── flake8                      # config file for linting
├── Makefile                    # Make file to help create docker images
├── requirements.txt            # requirements file for all dependencies
└── README.md                   # ...
```
