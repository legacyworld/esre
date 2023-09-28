FROM python:3.9-slim
WORKDIR /src
COPY . .
RUN pip3 install -r requirements.txt
ENV PYTHONUNBUFFERED 1
CMD [ "python3", "-u" , "app.py" ]
