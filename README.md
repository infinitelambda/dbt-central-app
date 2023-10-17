# dbt-central-app

## Problem Statement

Installing a dbt package is straightforward, but understanding and effectively utilizing the metadata produced by dbt packages can be challenging. Many data engineers and analytics engineers install packages, briefly check the tables, and often uninstall them due to a lack of insight into the package's value. Data engineers may struggle without access to BI dashboards, while analytics engineers might spend days trying to understand how to consume the data.

## Project Description

This application addresses the challenge of harnessing the power of dbt packages and their metadata. It aims to provide easy access to data produced by the semantic layer and dbt packages. The key objectives of this project are:

1. **Simplified Data Access:** With just the setup of your `dbt_cloud_api_key`, you can effortlessly access dashboards that display the output of dbt packages in a static way. This simplifies the data access process for data engineers and analytics engineers.

2. **Dashboard Customization:** For those who lack access to BI dashboards or need customized data views, this application offers the ability to create and maintain dashboards with visual representations of the dbt package outputs. Analytics engineers can create dashboards that align with their specific needs.

3. **DevOps Integration:** The application provides a solution for DevOps professionals to incorporate key performance indicators (KPIs) from dbt packages into their existing dashboards. This enables the monitoring of critical metrics and simplifies the process of ensuring data accuracy.

4. **Package Value Understanding:** By visualizing the data produced by dbt packages, users can better understand the value of each package. This helps in making informed decisions about whether to install, maintain, or uninstall a package.

In summary, this application streamlines the utilization of semantic layer and dbt package data, making it easily accessible for data engineers, analytics engineers, and DevOps professionals. It simplifies data access, allows for customization, and provides valuable insights into the output of dbt packages.

## Installation and Configuration

To run the application locally, follow these step-by-step instructions:

### 1. Setup Application Runtime

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/infinitelambda/dbt-central-app.git
   cd dbt-central-app
   ```

2. Create a virtual environment for the project. Replace `<venv_name>` with your preferred environment name (e.g., "myenv"):

   ```bash
   python3 -m venv <venv_name>
   ```

   Activate the virtual environment:

   ```bash
   source <venv_name>/bin/activate
   ```

3. Install the required Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### 2. Configure Application to Point to dbt Project

1. Open the `config.toml` file in the root directory of the project.

2. You can add your `dbt_cloud_api_key` in the configuration file to authenticate if you would like to use dbt cloud's API. Replace `<your_api_key>` with your actual API key:

   ```toml
   [dbt]
   dbt_cloud_api_key = "<your_api_key>"
   ```

### 3. Execute the Application

1. Navigate to the `src` directory:

   ```bash
   cd src
   ```

2. Once in the `src` directory, start the Streamlit application with the following command:

   ```bash
   streamlit run app.py
   ```

The application should now be running locally, and you can access it through your web browser.

### Dashboard User Guide

**Defining a Dashboard**

To define a dashboard in your application, follow these steps:

1. **Dashboard Name**: Choose a unique name for your dashboard.
   - Example: `Data Quality Tools Dashboard`

2. **Dashboard Title**: Set a title for your dashboard, which is displayed in the application.
   - Example: `Data Quality Overview`

3. **Dashboard Description**: Provide a description for your dashboard. You can include additional information or links.
   - Example:
     ```
     Make simple storing test results and visualization of these in a BI dashboard.
     👉 [Data Quality Tools](https://infinitelambda.github.io/dq-tools/)
     ```

4. **Package Name**: Specify the package name for your dashboard to organize it within your application.
   - Example: `dq-tools`

5. **Assets**: Define the assets that will be displayed on the dashboard. Each asset represents a specific metric or visualization.

   - **Asset Name**: Choose a unique name for the asset within the dashboard.
   - **Asset Title**: Provide a title for the asset displayed within the dashboard.
   - **Asset Type**: Specify the type of asset (e.g., "indicator," "table," "line_chart").
   - **Metrics**: List the metrics that should be displayed on the asset.

   Example:
   ```yaml
   assets:
     - name: Data Quality Score
       title: Data Quality Score
       description: Average value of `records_passed / records_scanned`
       metric: data_quality_score
       type: indicator

     - name: Data Quality Score over Time
       title: Data Quality Score over Time
       description: Average scoring every day
       metric: data_quality_score
       type: line_chart
       sort_by: METRIC_TIME__MONTH
       ascending: True
       x: METRIC_TIME__MONTH
       y: DATA_QUALITY_SCORE
   
     - name: dpe_undocumented_models_group_by
       title: Undocumented Models
       description: |
        `fct_undocumented_models` [(source)](https://github.com/dbt-labs/dbt-project-evaluator/blob/main/models/marts/documentation/fct_undocumented_models.sql) lists every model with no description configured.
        👉 Docs [dbt project evaluator docs](https://dbt-labs.github.io/dbt-project-evaluator/0.8/rules/documentation/#undocumented-models)
       metric: met_dpe_undocumented_models
       type: table
       group by: ent_fct_undocumented_models__resource_name,ent_fct_undocumented_models__model_type
   ```

6. Save your dashboard configuration.

### Asset User Guide

**Configuring Assets and Metrics**

Assets within a dashboard represent individual components displaying specific metrics or visualizations. To configure an asset, follow these steps:

1. **Asset Name**: Choose a unique name for the asset within the dashboard.
   - Example: `Data Quality Score`

2. **Asset Title**: Provide a title for the asset, which is displayed within the dashboard.
   - Example: `Data Quality Score`

3. **Asset Type**: Specify the type of asset, such as "indicator," "table," or "line_chart."

4. **Description**: Optionally, provide a description for the asset to offer additional context or information.

5. **Metrics**: Associate the asset with specific metrics by specifying the metric's name.

   Example:
   ```yaml
   metrics: data_quality_score
   ```

6. Depending on the asset type, you may have additional configuration options, such as "sort_by," "ascending," "x," and "y." Customize these as needed.

7. Save your asset configuration.

This guide should help you set up and run the application locally, accessing dbt project data effortlessly. If you have any questions or face issues during the setup, feel free to reach out for assistance.
