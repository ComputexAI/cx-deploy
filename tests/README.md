# Tests to validate app functionality

Run tests in Python or with Curl commands to test if the app is running

In a separate terminal, start the app:

To build and run the application locally, run the following commands in the root directory:


## Run the app locally:
Choose either of the two methods below to run the app locally:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Run Test
Open a second terminal to send requests to the API
```
# Run the python script
python test.py

# Run the bash script
bash test.sh
```