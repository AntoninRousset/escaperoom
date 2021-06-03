# escaperoom

## Requirements

### Build
* `pip install --user -r requirements.txt -c constraints.txt`
* `npm`
* `java-sdk`

### Run
* `pip install --user -r requirements.txt -c constraints.txt`


## Development
Set `DEBUG=on` in the dotenv.
1. `pip install --user -r requirements.txt -c constraints.txt`
2. `./manage.py runserver`

For frontend development, you may want to run concurrently the vite development server with `./manage.py watchfrontend --mode development`, running on port 3000.


## Production

1. `pip install --user -r requirements.txt -c constraints.txt`
3. `./manage.py buildfrontends`
4. `./manage.py collectstatic`
5. `./manage.py runserver`
