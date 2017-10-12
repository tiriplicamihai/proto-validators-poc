FROM python:2.7

RUN apt get update
RUN apt get install zip
RUN apt-get install vim

RUN curl -OL https://github.com/google/protobuf/releases/download/v3.2.0/protoc-3.2.0-linux-x86_64.zip
RUN unzip protoc-3.2.0-linux-x86_64.zip -d protoc3
RUN mv protoc3/bin/* /usr/local/bin/
RUN mv protoc3/include/* /usr/local/include/

RUN pip install protobuf
RUN pip install ipython
RUN pip install ipdb

RUN mkdir /opt/proto-validators

