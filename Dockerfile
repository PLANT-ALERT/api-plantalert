FROM python:3.9
WORKDIR /app
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app /app
CMD ["uvicorn", "fastapi:app", "--host", "0.0.0.0", "--port", "80"]
