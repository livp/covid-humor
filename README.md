# covid-humor
Research on Covid19 humor on Twitter

## Installation instructions
- Install Python 3.x (tested with 3.8)
- Install virtualenv

- Clone this repo
```shell script
git clone https://github.com/livp/covid-humor.git
cd covid-humor
```

- Create a new virtual environment 
```shell script
virtualenv venv
```

- Activate the new virtual environment. In Linux: 
```shell script
source venv/bin/activate
```

- In Windows:
```shell script
venv\Scripts\activate.bat
```

- Install dependencies:
```shell script
pip3 install -r requirements.txt
```

- Update the config.yaml file. Replace the access token values. Verify the desired keywords and sample sizes.

- Execute the application, replacing the values for date and output file:
```shell script
python application.py --date {YYYY-MM-DD} --output {outputfile.csv}
```



