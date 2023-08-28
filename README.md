# gcp-cloudbuild-guide

A guide on how to use GCP Cloud Build.

Contents:

- [GCP Cloud Build overview](#gcp-cloud-build-overview)
- [Prepare code and create cloudbuild yaml](#prepare-code-and-create-cloudbuild-yaml)
- [Connect your GCP project with a GitHub repository](#connect-your-gcp-project-with-a-github-repository)
- [Create Trigger for Cloud Build](#create-trigger-for-cloud-build)

## GCP Cloud Build overview

Google Cloud Build is a fully managed Continuous Integration/Continuous Deployment (CI/CD) platform offered by Google Cloud Platform (GCP). It is designed to help developers automate and streamline the process of building, testing, and deploying applications to the cloud.

**Capabilities:**

- Build Automation: Google Cloud Build allows you to define build pipelines using configuration files (such as YAML or JSON) called "build files." These pipelines automate the process of compiling, testing, and packaging your code.
- Flexible Build Environment: Cloud Build offers a wide range of build environments, including pre-configured build environments for popular programming languages and tools. You can also create custom build environments tailored to your specific needs.
- Integration with Version Control: Cloud Build integrates seamlessly with version control systems like Git. It can automatically trigger builds whenever code changes are pushed to your repository, ensuring that your application is built and tested consistently.
- Scalability: Cloud Build automatically scales to accommodate your build requirements. It can handle multiple builds simultaneously, allowing you to parallelize your build process and improve efficiency.
- Artifact Management: After a successful build, Cloud Build stores the resulting artifacts in the Google Cloud Storage, making it easy to manage and access the built binaries, libraries, or other output files.
- Customizable Workflows: You can define complex workflows with multiple build steps, tests, and deployment stages. This allows you to create a comprehensive CI/CD pipeline that encompasses everything from code validation to deployment.
- Integration with GCP Services: Cloud Build integrates with other Google Cloud services like Google Kubernetes Engine (GKE), App Engine, and Cloud Functions, enabling streamlined deployment of applications to these platforms.
- Security and Isolation: Builds are executed in isolated and secure environments, ensuring that one build does not interfere with another. Build images can also be customized to include necessary security measures.

Overall, Google Cloud Build is a powerful tool that simplifies and enhances your CI/CD process, ensuring efficient development workflows, faster delivery of features, and improved software quality.

## Prepare code and create cloudbuild yaml

Make sure you prepare your code that will be used by the gcp resources later on. In this example 2 cloud functions will be deployed as well as a Pub/Sub topic and a cloud scheduler. The cloud scheduler will trigger function A, function a will publish a message to the Pub/Sub topic and function B will subsrcibe to the topic and be triggered whenever there is a new topic message.
Then create the cloudbuild.yaml file. There you can specifiy which resources should be deployed. Keep in mind that all resources listed there will be deployed on every push by default. This can lead to errors if certain resources (e.g. Pub/Sub topic) already exist. Therefore you need to deploy resources like the Pub/Sub topic and the cloud scheduler separately.

- Pub/Sub topic deployment:

  General code snippet:

  ```shell
  gcloud pubsub topics <topic-name>
  ```

  Example code snippet:

  ```shell
  gcloud pubsub topics create github-topic
  ```

- Cloud scheduler deployment:

  General code snippet:

  ```shell
  gcloud scheduler jobs create http <schedule-name> \
  --schedule="0 4 * * *" \
  --http-method=POST \
  --uri="your-cloud-functions-url" \
  --message-body='{"project_id": "your-project-id", "bucket_name": "your-bucket", "topic_name": "your-topic"}' \
  --headers="Content-Type=application/json" \
  --attempt-deadline=1800s \
  --location='your-region' \
  --oidc--service-account-email=<service-acc-name>@<project-id>.iam.gserviceaccount.com
  ```

  Example code snippet:

  ```shell
  gcloud scheduler jobs create http github-func-a-scheduler \
  --schedule="0 4 * * *" \
  --http-method=POST \
  --uri="https://europe-west3-propane-nomad-396712.cloudfunctions.net/github-func-a" \
  --message-body='{"project_id": "propane-nomad-396712", "my_msg": "Hello World!"}' \
  --headers="Content-Type=application/json" \
  --attempt-deadline=1800s \
  --location='europe-west3' \
  --oidc-service-account-email=cloud-scheduler@propane-nomad-396712.iam.gserviceaccount.com
  ```

## Connect your GCP project with a GitHub repository

In order to connect a GitHub repository follow these steps:

1.  On GCP go to Cloud Build and make sure the Cloud Build service account has the necessary permissions by checking the _Settings_ tab. If you want to deploy cloud functions the following permissions are needed:

    - Cloud Functions Developer
    - Cloud Run Admin (For gen2 cloud functions)

    To get started quickly you can grant access to all service accounts when asked.

2.  Go to _Repositories_ tab choosed 2nd gen and click link repository. In the _Connection_ field click _CREATE HOST CONNECTION_. A new page will open and there you can select the provided (e.g. GitHub). Choose a region (**use erope-west1 or any other region from this [list](https://cloud.google.com/build/docs/locations#restricted_regions_for_some_projects) if you use the free GCP version**) and a name. In case _Secret Manager API is not enabled_ go to _API's and Services_ --> _Enabled API's and services_ --> _ENABLE APIS AND SERVICES_ --> Search for "Secret Manager API" and enable it. Now connect with GitHub.

    **Note:** It may take a few minutes until the API is fully enabled and GCP can successfully connect with GitHub.

3.  You have the option to grant access to all repositories or only to selection of repos. Choose whatever you prefer. After that you should see your GitHub account/repo listed in the _Repositories_ tab.

## Create Trigger for Cloud Build

1.  Now go to _Triggers_ and create a new trigger. Choose a name, region and an Event on which cloud build is triggered (e.g. _push to branch_). Select 2nd gen as the source and choose a repository. Your default branch will be selected automatically. You can also select your own service account that will be used to deploy your resources. If nothing is specified the default cloud build service account will be used.

2.  If not done already enable the _Cloud Resource Manager API_ or your builds will fail. In case your builds will fail later on you can try giving the service account that is used by cloudbuild the serviceAccountTokenCreator role.

    General code snippet:

    ```shell
    gcloud projects add-iam-policy-binding <project-id> \
        --member=serviceAccount:<your-service-acc>@gcp-sa-pubsub.iam.gserviceaccount.com \
        --role=roles/iam.serviceAccountTokenCreator
    ```

    Example code snippet:

    ```shell
    gcloud projects add-iam-policy-binding propane-nomad-396712 \
        --member=serviceAccount:service-973117053722@gcp-sa-pubsub.iam.gserviceaccount.com \
        --role=roles/iam.serviceAccountTokenCreator
    ```

3.  Whenever you push any changes to the repo cloud build will automatically trigger and deploy the resources specified in the cloudbuild.yaml file. However cloudbuild has some major downsides:

    - The trigger is very generic and can't be fine tuned (as of August 2023). This means any kind of change in this repo will trigger the cloud build function even if you only update the readme. It is currently not possible to exclude certain files for the trigger condition.
    - There is no conditional deployment. Many resources like Pub/Sub topics can't be deployed if they already exist but there is no native way to check if certain resources already exist and only deploy resources that do not exist yet (unless you use some very janky bash scripting as workaround which is not recommended).

      If you need conditional deployment in your CI/CD pipeline you should use a different service like GitHub Actions or Jenkins instead.
