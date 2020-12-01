FROM python:3.6

WORKDIR /usr/src/app

COPY . .

RUN pwd

RUN ls .


RUN wget https://github.com/bantucaravan/temp_ci_app/raw/master/app.tar.gz
RUN tar -xzvf app.tar.gz
RUN pip install --no-cache-dir -r app/requirements.txt
CMD [ "python", "app/main.py" ]
