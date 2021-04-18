# Dependencies
* Docker

# Running the app
```bash
bash run-app.sh
curl localhost:8000/drop_token
```

# Running the unit tests
```bash
bash run-unit-tests.sh
```

# Running the functional tests
```bash
bash run-functional-tests.sh
```

# Notes
- Testing edge cases isn't very thorough in the interest of time.
- FastAPI by default returns 422 instead of 400 for invalid payloads. This behavior is overridden to meet requirements.
- Winning condition is controlled by an environment variable, not hardcoded (twelve-factor app).
- Because state is all in memory, this service is not horizontally scalable. One solution is to persist state in a NoSQL database and have stateless instances of the server connect to it.
