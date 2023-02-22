# Dockerfile
## Build venv
FROM python:3.10-slim-buster as build

# set work directory
WORKDIR /var/www/stox-app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies

# The `--copies` option tells `venv` to copy libs and binaries
# instead of using links (which could break since we will
# extract the virtualenv from this image)
RUN python -m venv --copies /var/www/stox-app/venv

# Make sure we use the virtualenv:
ENV PATH="/var/www/stox-app/venv/bin:$PATH"

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt


## Beginning of runtime image
# Remember to use the same python version
# and the same base distro as the venv image
FROM python:3.10-slim-buster as prod

# set environment variables
ENV HOST 0.0.0.0

COPY --from=build /var/www/stox-app/venv /var/www/stox-app/venv/
ENV PATH /var/www/stox-app/venv/bin:$PATH

# copy project
WORKDIR /var/www/stox-app
COPY ./src ./src


# run development server
CMD uvicorn src.server:app --host $HOST --port $PORT --reload