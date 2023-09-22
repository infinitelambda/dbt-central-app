# dbt Dashboards Streamlit

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
Navigate to the src directory and once the dependencies are installed, you can start the streamlit application using the following command:
```commandline
streamlit run app.py
```

# Use the POC for transpose table
Follow the previously described setup steps then:  
From the root directory **dbt-dashboards-strimlit/** run

```commandline
streamlit run transpose_df.py
```

# Use **_mf_helper.py_**

## To automatically generate all the cache files _(.csv)_ please use this script as follows:
Follow the previously described setup steps then:  
Navigate to your dbt_project directory where the profiles.yml is located. 

Please make sure that in _```mf_helper.py```_:
- ```dashboard_path_to_load``` is pointing to the desired YAML file
- ```self.root_directory``` is pointing to the desired location

Make sure that you use **username** and **password** in the _profiles.yml_. **It's critical for metricflow to run seamlessly**

Run the script from you using:  
```commandline
python path/to/mf_helper.py
```

### Note:  
_This is currently an experimental version for manual testing.  
Running metricflow directly from the dbt project to validate the success of the given YAML specification is advised.  
```mf_helper.py``` will show the result of execution in a byte format.  
All the progress will be implemented in the main branch of the project repository after approval_  
  
**Please make sure all the manual steps are done before running.** 
