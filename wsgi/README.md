* Create /var/log/<name of app> and set the path in the site definition
* expects the wsgi file in /var/www/peer/peer.wsgi iirc: /var/www/<name of app>/<name of app>.wsgi
* code goes in /var/www/<name of app>/<name of app>/
* expects user wsgi, whom must be a member of www-data.
* Set owner and user of /var/www/<name of app>/<name of app> to wsgi:www-data recursively
* make sure tmp directory is writeable and located where peer.py or whatever the main python file's name becomes. /var/www/<name of app>/<name of app>/tmp
* make a floppy link from conf in sites-available to conf in sites-enabledy

