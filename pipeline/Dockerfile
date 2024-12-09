FROM python:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt


COPY etl_pipeline.py .


CMD ["python3", "etl_pipeline.py"]