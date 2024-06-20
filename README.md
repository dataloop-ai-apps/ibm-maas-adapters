# IBM Watsonx as a Service - Model Adapters

This repository contains the code for Dataloop model adapters that invoke models served in IBM via their API.

More information on IBM Watsonx as a Service can be
found [here](https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/welcome-main.html?context=wx&audience=wdp).

The apps in this repository are designed to interface with IBM models served via API endpoints. These adapters
facilitate the integration and interaction with IBM's machine learning models and Dataloop platform.

To use this models in Dataloop Platform you'll need the following:

1. **Dataloop Account**
2. **IBM Cloud Account**: Access to IBM Cloud services is required to deploy and manage these models.
3. **API Key**: Can be created in your IBM Account.
4. **Project id** : A valid id of a project in your IBM account.

## Install in Dataloop Platform

Once you have an API key and a Url you can access and get a response from your model in Dataloop platform.

### 1. Install the model from Dataloop Marketplace

Go to Marketplace, Models tab, and search for the requested model (IBM and Model's name) and install:

![Get API Key and Endpoint URL](assets/marketplace.png)

### 2. Edit the Region and Project-id in the model's configuration

#### 2.1 On model's configuration edit `project-id` and `region`:

Navigate to Model management tab, and click on the installed model:

![Get API Key and Endpoint URL](assets/model-managment.png)

Insert your `project-id` and `region` and click `Save`

![Get API Key and Endpoint URL](assets/configuration.png)

#### 2.2 On Data Governance tab, add your API key:

1. Click on create integration and choose `create secret`

![Get API Key and Endpoint URL](assets/data-govarnece.png)

2. Choose a `secret name` an insert your API key.

![Get API Key and Endpoint URL](assets/save-secret.png)

### 3. Add secret name to the service

* In your pipeline, click on the Model node and choose `edit service configuration`

![Get API Key and Endpoint URL](assets/service settings.png)

* In `init inputs value`, edit `ibm_api_key_name` and insert your secret name. In `Secrets & Integrations` insert
  your secret by choosing from the options list.

![Get API Key and Endpoint URL](assets/insert-secret.png)

![Get API Key and Endpoint URL](assets/insert-secret-name.png)


After following these steps, you be able to use Azure Serverless API models via Dataloop Platform.