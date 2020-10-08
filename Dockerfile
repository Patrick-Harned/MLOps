FROM python:3.6

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "python pipeline/main.py scikit-learn_0.22-py3.6 mlops data.csv" ]
