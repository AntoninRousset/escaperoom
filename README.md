# escaperoom

## To run
0. `cd escaperoom`
1. `pip install --user -r requirements.txt -c constraints.txt`
3. `./manage.py buildfrontend`
4. `./manage.py collectstatic`
5. `./manage.py runserver`

For developpement, set `DEBUG=on` in the `escaperoom/.env` file. You can run
`./manage.py buildfrontend --watch` to continuously build the frontend.
