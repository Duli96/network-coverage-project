FROM python:3.8

WORKDIR /network-coverage-app
ENV VAR1=10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install & use pipenv
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy
EXPOSE 9090

#     pip uninstall -y pipenv
COPY ./app ./app
COPY ./alembic ./alembic
COPY .env .
COPY .gitignore .
COPY  alembic.ini .
COPY run.py .



CMD ["python","run.py"]