#! bin/bash

mkdir ~/gdocs
cd ~/gdocs
wget http://gdata-python-client.googlecode.com/files/gdata-2.0.17.tar.gz
tar -zxvf gdata-2.0.17.tar.gz
cd gdata-2.0.17

sudo python setup.py install
sudo apt-get install python-setuptools
sudo apt-get install python-tk
sudo easy-install sphinx

