# Dbt Dashboards Strimlit

## Usage

### Clone the Repository: 
Start by cloning this repository to your local machine using the following command:
```commandline
git clone https://gitlab.infinitelambda.com/ilrun/dbt-dashboards-strimlit.git
```
then
```commandline
cd dbt-dashboards-strimlit
```
### Create a Virtual Environment:
Run the following command to create a virtual environment. Replace <venv_name> with the name you want to give to your virtual environment (e.g., "myenv").

```commandline
python -m venv <venv_name>
```

Example:

```commandline  
python -m venv .venv
```

This command will create a new directory with the specified name (e.g., ".venv") in your project folder.

### Activate the Virtual Environment:

```commandline  
source .venv/bin/activate
```

Once activated, your terminal prompt should change, indicating that you are now in the virtual environment.

### Install Dependencies:

Install the necessary Python dependencies:
```commandline
pip install -r requirements.txt
```

### Run the Application: 
Navigate to the src directory and once the dependencies are installed, you can start the Streamlit application using the following command:
```commandline
streamlit run app.py
```

# Use the POC for transpose table

From the root directory (**dbt-dashboards-strimlit/**) run

```commandline
streamlit run transpose_df.py
```

# Use **_mf_helper.py_**

## To automatically generate all the cache files (_.csv_) please use this script as follows:

Navigate to your dbt_project directory where the profiles.yml is located. 

Please make sure that in _```mf_helper.py```_:
- ```self.file_path``` is pointing to: "dbt-dashboards-strimlit/adrien/dashboard/dbt_project_evaluator.yml"
- ```self.root_directory``` is pointing to "dbt-dashboards-strimlit/adrien/"

Make sure that you use **username** and **password** in the _profiles.yml_. **It's critical for metricflow to run seamlessly**

Run the script from you using:  
```commandline
python path/to/dbt-dashboards-strimlit/mf_helper.py
```


