FROM python:3.9-slim-buster

WORKDIR app

RUN apt-get update && apt-get -y install gcc mono-mcs && apt-get install libzbar0 -y && pip install pyzbar && pip install pillow
RUN apt-get install ffmpeg libsm6 libxext6 git libpq-dev -y
RUN pip install torch --no-cache-dir

COPY ./ /app
COPY ./migrations /app/bot/
COPY ./media /app/bot/
COPY ./video /app/bot/

RUN pip install -r requirements.txt
RUN chmod +x ./run.sh
CMD ./run.sh