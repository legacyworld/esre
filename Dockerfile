FROM python:3.9-slim

RUN pip3 install elasticsearch openai flask python-dotenv
ENV PYTHONUNBUFFERED 1
WORKDIR /src
CMD [ "python3", "-u" , "app.py" ]
