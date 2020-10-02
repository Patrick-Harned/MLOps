FROM node

WORKDIR /usr/src/app

COPY . ./

RUN npm install --global smee-client

CMD [ "smee", "--url", "https://smee.io/O5CdqEnbTM78ea9J", "--path", "/bitbucket-webhook/" ]


