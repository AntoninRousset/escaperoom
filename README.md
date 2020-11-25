# escaperoom

## To run
0. cd escaperoom
1. pip install --user -r [requirements.txt](/requirements.txt)
2. rc-service postgresql start
3. ./manage.py buildfrontend --log
4. ./manage.py runserver

For developpement you can use `./anage.py watchfrontend --log escaperoom` to
continuously build the frontend for the `escaperoom` app.
