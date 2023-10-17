FROM python:3.8-alpine
WORKDIR /app
COPY ./app /app
RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3" , "main.py"]