# gcp-cloudbuild-guide

A guide on how to use GCP Cloud Build.

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

Make sure you prepare your code that will be used by the gcp resources later on.
Then create the cloudbuild.yaml file. There you can specifiy which resources should be deployed. Keep in mind that all resources listed there will be deployed on every push by default. This can lead to errors if certain resources (e.g. Pub/Sub topic) already exist. Therefore you need to include checks and conditions wheter a resource should be deployed or not. This could be done like this:

```yaml
steps:
  # 0. Check if resources should be deployed
  - name: "gcr.io/cloud-builders/gcloud"
    args: ["pubsub", "topics", "describe", "github-topic"]
    id: check-topic
    ignoreErrors: true

  # 1. Create new Pub/Sub topic
  - name: "gcr.io/cloud-builders/gcloud"
    args: ["pubsub", "topics", "create", "github-topic"]
    condition: steps.check-topic.results.returnCode != 0 # Only deploy if topic doesn't exist
```

Also you might want to exclude certain files like README.md from triggering the cloud build yaml every time it is updated.
This can be done like this:

```yaml
# Define the affected branches
substitutions:
  _BRANCH: ".*" # Match all branches by default

# Trigger only on pushes that modify files other than the README
trigger:
  branch: $_BRANCH
  event: push
  files:
    - "**/*.*"
  excludedFiles:
    - "**/README.md"
```

## Connect your GCP project with a GitHub repository

In order to connect a GitHub repository follow these steps:

1.  On GCP go to Cloud Build and make sure the Cloud Build service account has the necessary permissions by checking the _Settings_ tab. If you want to deploy cloud functions the following permissions are needed:

    - Cloud Functions Developer
    - Cloud Run Admin (For gen2 cloud functions)

    To get started quickly you can grant access to all service accounts when asked.

2.  Go to _Repositories_ tab choosed 2nd gen and click link repository. In the _Connection_ field click _CREATE HOST CONNECTION_. A new page will open and there you can select the provided (e.g. GitHub). Choose a region (e.g. _europe-west3_) and a name. In case _Secret Manager API is not enabled_ go to _API's and Services_ --> _Enabled API's and services_ --> _ENABLE APIS AND SERVICES_ --> Search for "Secret Manager API" and enable it. Now connect with GitHub.

    **Note:** It may take a few minutes until the API is fully enabled and GCP can successfully connect with GitHub.

3.  You have the option to grant access to all repositories or only to selection of repos. Choose whatever you prefer. After that you should see your GitHub account/repo listed in the _Repositories_ tab.

4.  Now go to _Triggers_ and create a new trigger. Choose a name, region and an Event on which cloud build is triggered (e.g. _push to branch_). Select 2nd gen as the source and choose a repository. Your default branch will be selected automatically. You can also select your own service account that will be used to deploy your resources. If nothing is specified the default cloud build service account will be used.
