FROM python:3.6

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN  ls pipeline
#CMD [  "python", "pipeline/main.py", "scikit-learn_0.22-py3.6", "mlops", "data.csv" ]
CMD [ "python", "pipeline/main.py", "scikit-learn_0.22-py3.6", "mlops", "val_breast_cancer.csv" ]
