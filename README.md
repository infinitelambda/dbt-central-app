# dbt Dashboards Streamlit

## Usage

### Clone the Repository

Start by cloning this repository to your local machine using the following command:

```commandline
git clone https://gitlab.infinitelambda.com/ilrun/dbt-dashboards-strimlit.git
```

then

```commandline
cd dbt-dashboards-strimlit
```

### Create a Virtual Environment

Run the following command to create a virtual environment. Replace <venv_name> with the name you want to give to your virtual environment (e.g., "myenv").

```commandline
python3 -m venv <venv_name>
```

Example:

```commandline  
python3 -m venv .venv
```

This command will create a new directory with the specified name (e.g., ".venv") in your project folder.

### Activate the Virtual Environment

```commandline  
source .venv/bin/activate
```

Once activated, your terminal prompt should change, indicating that you are now in the virtual environment.

### Install Dependencies

Install the necessary Python dependencies:

```commandline
pip install -r requirements.txt
```

### Run the Application

Navigate to the src directory and once the dependencies are installed, you can start the streamlit application using the following command:

```commandline
streamlit run app.py
```

If you would like to enable Semantic API calling, please make sure to:

- Set value for the environment variable named `DBT_SEMANTIC_URL`

```bash
export DBT_SEMANTIC_URL="jdbc:arrow-flight-sql://semantic-layer.cloud.getdbt.com:443?environmentId=?&token=?" 
# replace ? with your value
```

- Set query of the metric (in Dashboard yml) instead of metric name:

```yml
dashboards:
  - name: Dashboards for tesing Semantic API
    ...
    assets:
      - name: Test Coverage
        ...
        metric:
          query: select * from {{ semantic_layer.query(metrics=["dbt_project_evaluator_test_coverage"]) }}
```

## Load Data

### To automatically generate all the cache files _(.csv)_ please use the Data Loader menu from the sidebar

## Note

_This is currently an experimental version for manual testing.  
Running metricflow directly from the dbt project to validate the success of the given YAML specification is advised.  
```mf_helper.py``` will show the result of execution in a byte format.  
All the progress will be implemented in the main branch of the project repository after approval_  
  
**Please make sure all the manual steps are done before running.**
