FROM ubuntu:18.04

MAINTAINER Toshiki Tsuboi <t.tsubo2000@gmail.com>

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install apt packages
RUN apt-get update \
 && apt-get install -y \
      git-core \
      python-dev \
      libxslt1.1 \
      libxml2-dev \
      libssl-dev \
      libxslt-dev \
      libffi-dev \
      python-gevent \
      python-greenlet \
      python-thrift \
      python-bitarray \
      python-bottle \
      python-psutil \
      python-kazoo \
      python-heatclient \
      libmysqlclient-dev \
      iptables \
      iproute2 \
      vim \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# install pip
WORKDIR /
ADD https://bootstrap.pypa.io/pip/2.7/get-pip.py /
RUN python get-pip.py \
 && pip install pip

# install heat
RUN git clone https://github.com/openstack/heat.git /opt/heat \
 && cd /opt/heat \
 && git checkout -b mitaka-eol mitaka-eol \
 && pip install pbr==1.3 \
 && pip install -r requirements.txt \
 && pip install -e . \
 && pip install mysql-python==1.2.5 \
 && pip install SQLAlchemy==1.4.0

# deploy heat.conf
COPY ./heat.conf /etc/heat/heat.conf

# deploy python script
WORKDIR /
RUN git clone https://github.com/ttsubo2000/study-of-sqlalchemy-migrate.git /work
WORKDIR /work

EXPOSE 8004
