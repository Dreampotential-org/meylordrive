build:
	sudo docker build --tag meylorci .

run:
	sudo docker run --name meylorci -p 8000:8000 -d meylorci

run-dev:
	sudo docker run --name meylorci -p 8000:8000 meylorci

logs:
	sudo docker logs meylorci -f

start:
	 sudo docker run --rm -it meylorci alembic upgrade head && sudo docker start meylorci

stop:
	sudo docker stop meylorci

remove:
	sudo docker container rm meylorci
