FROM golang:1.19-bullseye as dev

# allows for hot-reloading in dev
RUN go install github.com/beego/bee/v2@latest

# ENV GO111MODULE=on
# ENV GOFLAGS=-mod=vendor

ENV APP_HOME /var/www/stox-app
RUN mkdir -p "$APP_HOME"

WORKDIR "$APP_HOME"

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY ./src ./src
WORKDIR /"$APP_HOME"/src

CMD ["bee", "run"]