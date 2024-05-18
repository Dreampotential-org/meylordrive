sudo apt-get update && sudo apt-get install -y python3-virtualenv python3-pip libpq-dev  postgresql-common gdal-bin postgis postgresql-server-dev-all postgresql-postgis --fix-missing

sudo apt-get install -y wget libpq-dev mtools unzip
sudo apt-get install -y ssh git portaudio19-dev python3-pyaudio alsa-utils


wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
sudo sh -c 'tar -x geckodriver -zf geckodriver-v0.33.0-linux64.tar.gz -O > /usr/bin/geckodriver'
sudo chmod +x /usr/bin/geckodriver
rm -fr geckodriver-v0.33.0-linux64.tar.gz


wget https://chromedriver.storage.googleapis.com/92.0.4515.107/chromedriver_linux64.zip
unzip chromedriver_linux64.zip

sudo mv chromedriver /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
