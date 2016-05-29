FROM ubuntu:latest
MAINTAINER Frank <316345420@qq.com>

RUN apt-get update
RUN apt-get install -y  build-essential
#ENV https_proxy=https://10.144.1.10:8080
#ENV http_proxy=http://10.144.1.10:8080
RUN apt-get install -y python-setuptools libxml2-dev libxslt-dev  libbz2-dev  python-dev
RUN easy_install pip

RUN apt-get install -y gfortran libopenblas-dev liblapack-dev
RUN apt-get install -y pkg-config
RUN apt-get install -y wget
RUN apt-get install -y git

RUN pip install numpy
RUN pip install scipy
RUN pip install pandas
RUN pip install patsy
RUN pip install statsmodels
RUN apt-get install -y libfreetype6-dev; \
        pip install matplotlib
RUN pip install ws4py
RUN pip install tornado
RUN pip install tweepy
RUN pip install cython

# TA-Lib
RUN cd /tmp; \
        wget http://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz; \
        tar -xzf ta-lib-0.4.0-src.tar.gz; \
        cd ta-lib; \
        ./configure ; make; make install; \
        cd ..; \
        rm ta-lib-0.4.0-src.tar.gz; \
        rm -rf ta-lib
RUN pip install TA-Lib

RUN cd /tmp; \
        wget http://sourceforge.net/projects/boost/files/boost/1.60.0/boost_1_60_0.tar.gz \
        tar -xzvf boost_1_60_0.tar.gz; \
        cd /tmp/boost_1_60_0; \
        ./bootstrap.sh --prefix=/usr/local; \
        ./b2 install --prefix=/usr/local; \
        cd ..; \
        rm -rf boost_1_60_0
		
RUN pip install lxml
RUN pip install tushare
RUN pip install jupyter 

RUN cd /root; \
    git clone https://github.com/Yam-cn/pyalgotrade-cn.git

WORKDIR /root/pyalgotrade-cn/

ENV PYTHONPATH=/root/pyalgotrade-cn/
ENV LD_LIBRARY_PATH=/root/pyalgotrade-cn/pyalgotrade/CTP/api/

EXPOSE 8888

ENTRYPOINT nohup /usr/local/bin/jupyter notebook --ip=0.0.0.0