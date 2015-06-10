# Fatracker

Small app based on Flaskr to track your weight

## Installation
	
	git clone https://github.com/khrogos/fatracker
	cd fatracker
	pip install -r requirements.txt
	cp settings.sample.cfg settings.py

personnalized settings.py with your informations

And do : 

	python fatracker.py

Enjoy at http://your.ip:5000

You need to login to start posting data. 

## deploy with web server

exemple of nginx host : 

	upstream flaskserver {
	    server 0.0.0.0:5000;
	}

	server {
	        server_name your.domain.tld;
	        location / {
        		proxy_pass http://flaskserver;
		        proxy_redirect off;
		        proxy_set_header Host $http_host;
		        proxy_set_header X-Real-IP $remote_addr;
		        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	        	proxy_read_timeout 300s;
	        }
	}

restart nginx and it's done !
