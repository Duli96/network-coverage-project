
# Network Coverage Project

This is a RESTful API that developed using python and aiohttp. The API has included CRUD operations regarding a Tower Network which contains a Center Hub, Regional Hubs and Towers. 


## API Reference

#### Get all network details

```http
  GET /api/network
```

#### Add new network details into the database

```http
  POST /api/network
```

| Request Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Graph File`      | `string` | **Required**. The .graphml file which contained the Tower Network details  |
                            
#### Get network coverage for a given location

```http
  GET /api/network/{latitude}/{longitude}
```

| Parameters | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `latitude`      | `number` | **Required**. Latitude of the location |
| `longitude`      | `number` | **Required**. Longitude of the location |

#### Calculate the cost to build a given Tower Network

```http
  POST /api/network/cost
```

| Request Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Network id`      | `number` | **Required**. Id of the network to be built |
| `Cost File`      | `number` | **Required**. The .json file that contained the cost values |

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`POSTGRES_USER`
`POSTGRES_PASSWORD`
`POSTGRES_HOST`

`POSTGRES_PORT`
`POSTGRES_DB`
`SECRET_KEY`


## Installation

This project requires pipenv for setting up the environment. 
You should have installed python and pip before installing pipenv

- Installing pipenv into your home directory
```bash
  pip install --user pipenv
```

- Open a new terminal with pipenv activated
```bash
  pipenv shell
```

- Install libraries that requires for the project
```bash
  pipenv install
```
    
## Using Alembic
Alembic has used in this project to create database tables inside the database

- To setup Alembic go to the main folder of the project and run:
```bash
  pip install --user pipenv
```

- Open a new terminal with pipenv activated
```bash
  pipenv shell
```

- Install libraries that requires for the project
```bash
  alembic init alembic
```

- Inside the `alembic.ini` file in your project directory, change the `sqlalchemy.url =` property with your database credentials
```bash
  sqlalchemy.url = postgres://{{username}}:{{password}}@{{address}}/{{db_name}}
```

- Inside the `env.py` file in your alembic directory, import db object and set the `target_metadata =` to db object.
```bash
  from app.models.models import db
  target_metadata = db
```
- Create first migration revision with Alembic.
```bash
 alembic revision -m "first migration" --autogenerate --head head
```
- Apply migration on database and create tables according to the defined db models
```bash
 alembic upgrade head
```



    
## Run Project

- Start the server

```bash
  pipenv run python run.py
```
- Open swaggerUI in browser

```bash
  http://localhost:9090/api/ui/
```


## Running Tests

Testcases for this project has been implmented using pytest.

```bash
  python3 -m pytest
```

