# Good practices
- Any object with a background running service must not start it service during init but using a method `start()` and must be stopped using a method `stop()`. This pratice avoid to mix between configuration and execution, and allows a specific service to be rerun in case of failure.

## Testing
- good to test if still working when executed using a symbolic link

# Logging
- According to [logging section of the python docs](https://docs.python.org/3/howto/logging.html#advanced-logging-tutorial), it is a good convention to use `logger = logging.getLogger(__name__)`.
- According to the [Logging chapter of The Hitchiker's guide to Python](https://docs.python-guide.org/writing/logging/), there is three ways to configure a logger:
  - Using an INI-formatted file
  - Using a dictionary or a JSON-formatted file
  - Using code


