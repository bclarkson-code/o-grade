from python:3.10

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
