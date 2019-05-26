# Use an official Python runtime as a parent image
FROM ubuntu:16.04

MAINTAINER DurkoMatko "nitramdurcek@gmail.com"

RUN apt-get update -y && \  
    apt-get install -y python-pip

COPY ./requirements.txt /requirements.txt

WORKDIR /
RUN apt-get -y install libc-dev
RUN apt-get -y install build-essential
RUN pip install -U pip
RUN apt-get install -y python-tk
RUN apt install -y python-numpy
RUN apt-get install -y python-matplotlib
RUN pip install -r requirements.txt
RUN pip install -U scikit-learn scipy matplotlib
RUN apt-get install -y libxml2-dev
RUN apt-get install -y libxslt1-dev
RUN apt-get install -y python-dev

COPY . /

ENTRYPOINT [ "python2.7" ]

CMD [ "app/app.py" ]  






#RUN mkdir -p /opt/app/
#WORKDIR /opt/app/

#COPY requirements.txt /opt/app/requirements.txt

#RUN pip install -r requirements.txt
#RUN sudo apt-get install python-matplotlib

#COPY . /opt/app

# Run Sentiment_Analyzer_Gui.py when the container launches
#CMD ["python", "./app.py"]
