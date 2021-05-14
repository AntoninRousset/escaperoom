# escaperoom

## Requirements

### Build
* `pip install --user -r requirements.txt -c constraints.txt`
* `npm`
* `java-sdk`

### Run
* `pip install --user -r requirements.txt -c constraints.txt`


## Frontend development
Set `DEBUG=on` in the dotenv.
1. `pip install --user -r requirements.txt -c constraints.txt`
2. `./manage.py buildfrontends`
3 `./manage.py runserver &`
4 `npm run --prefix=./escaperoom/frontend dev`


## Production

1. `pip install --user -r requirements.txt -c constraints.txt`
3. `./manage.py buildfrontends`
4. `./manage.py collectstatic`
5. `./manage.py runserver`
