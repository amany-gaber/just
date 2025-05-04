# Project

project description

## Table of content

- [Project](#Project)
  - [Table of content](#table-of-content)
  - [Development](#development)
    - [Prerequisites](#prerequisites)
    - [Configuration](#configuration)
    - [Run instructions](#run-instructions)
  - [Docker instructions](#docker-instructions)
    - [For Development](#for-development)
    - [For Production](#for-production)
      - [Build image](#build-image)
      - [Publish image](#publish-image)
  - [API Details](#api-details)
  
## Development

### Prerequisites

- Python v3.12

### Configuration

- Adapt `.env`

### Run instructions

- Create a virtual environment and install dependencies

```sh
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Load env variables (config)

```sh
# For windows
set -a && source ../.env && set +a
```
```sh
# For linux
source ../.env
```

- Start the server

```sh
cd src
python main.py
```

- Lint src dir

```sh
flake8 src
```


## Docker instructions

### For Development

- Start container

```sh
docker-compose -f docker-compose.yml up -d
```

- End container

```sh
docker-compose -f docker-compose.yml down
```

- Connect to it

```sh
docker-compose -f docker-compose.yml exec api sh
```

- Verify logs file for the api

```sh
docker-compose -f docker-compose.yml logs api
```

### For Production
#### Build image

```sh
make build
```

#### Publish image

```sh
make publish
```


## API Details

- [API Details](./api/README.md)

```
cd ..
docker compose up -d
docker ps
docker compose logs api
```
