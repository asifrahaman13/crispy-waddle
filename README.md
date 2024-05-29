## About the application

- First pull the repository. `git clone https://github.com/asifrahaman13/crispy-waddle.git`

- Go to the root directory. `cd sentiment`

- create a virtual environment. `virtualenv .venv`

- Now install the dependencies. `pip install -r requirements.txt`

- Now rename the .env.example. `mv .env.example .env`. 

- Give the proper configuration by giving the API keys. For example set the open ai key, mapbox api key etc.

- Next you need to run the application using the following script: `python3  src/main.py`

## Want to run in docker?

First you need to build the docker container:

`docker build -t sentiment:latest`

Ensure that you have set the OPENAI_API_KEY, and MONGO_URI

```bash
export OPENAI_API_KEY=<your api key>
export MONGO_URI=<mongodb connection string. localhost wont work. Please use mongodb atlas>
```

Next run the docker container:
`sudo docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -e MONGO_URI=$MONGO_URI sentiment:latest`

