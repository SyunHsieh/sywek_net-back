FROM ubuntu:latest as base
    

    RUN apt-get -y update
    RUN mkdir /opt/flask-tu

    COPY requirements.txt /opt/flask-tu/
    WORKDIR /opt/flask-tu/
    RUN apt-get update 

    RUN apt-get install -y tzdata
    RUN echo “Asia/Taipei” > /etc/timezone
    RUN dpkg-reconfigure -f noninteractive tzdata

    RUN apt-get install -y iputils-ping

    RUN apt-get install wait-for-it
    #RUN ln -fs /usr/share/zoneinfo/Asia/Taipei /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

    FROM base as pytoolsinstall
    RUN apt-get install -y python3.7
    RUN apt-get install -y python3-pip

    RUN pip3 install --upgrade pip
    RUN apt-get install -y postgresql
    RUN apt-get install -y libpq-dev
    RUN pip3 install -r requirements.txt
    ENV FLASK_APP=main.py

    COPY . /opt/flask-tu/
    WORKDIR /opt/flask-tu
    
    #FROM base as debug
    #CMD python3 -m ptvsd --host 0.0.0.0 --port 5678 --wait --multiprocess -m flask run -h 0.0.0.0 -p 9000
    #CMD python3 -m ptvsd --host 0.0.0.0 --port 5678 --wait gunicorn -b 0.0.0.0:9000 main:app
    #FROM base as run
    #WORKDIR /opt/flask-tu
    #CMD flask run -h 0.0.0.0 -p 9000
    #WORKDIR /opt/flask-tu
    #RUN apt-get install net-tools
    
    #CMD ["gunicorn", "-b", "0.0.0.0:9000", "main:app"]



