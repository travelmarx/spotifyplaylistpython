# A Python web app that displays Spotify playlists

This Python web app reads a Spotify playlist ID and returns a visual and textual summary of the tracks in the playlist. It uses [Flask](https://flask.palletsprojects.com/en/2.1.x/), a micro web framework written in Python.

For an example of this code in action, see the blog post [Visualizing a Spotify Playlist - Simple Python Flask Web App Container Running Locally or in Azure](https://blog.travelmarx.com/2022/09/visualizing-spotify-playlist-simple-python-flask-web-app-container.html).

The code was designed for use in Azure, running as a container in App Service (free tier service). (Specifically, the Python web app code is built into a Docker container and run on App Service.) However, the code is general enough to be used with other cloud services or situations. Or, you can just run the code locally and still read playlists without deploying the code to a cloud service.

We also show how to run this sample code as well as what went into building the sample, if you are curious. The [Spotipy](https://spotipy.readthedocs.io/en/master/) lightweight Python library is used to interface with Spotify's Web API. It requires a client id and secret, which you can get from the [Spotify Web API Tutorial](https://developer.spotify.com/documentation/web-api/quick-start/).

Sections:

* [Build in Azure and deploy to App Service with Azure Container Registry](#build-in-azure-and-deploy-to-app-service-with-azure-container-registry) - Cost: a few dollars a month in Azure.

* [Build in Azure and deploy to App Service with Managed Identity to Access Azure Container Registry](#build-in-azure-and-deploy-to-app-service-with-managed-identity-to-access-azure-container-registry) - Cost: a few dollars a month in Azure.

* [Build and deploy to App Service with Docker Hub](#build-and-deploy-a-app-service-with-docker-hub) - Cost: 0. Uses free tier App Service and Docker Hub (personal) to host image won't cost anything in either services.

* [Build and run locally in a container](#build-and-run-locally-in-a-container) - Cost: 0. Doesn't use Azure or Docker Hub. You must have Docker installed locally.

* [Build and run locally in a virtual environment](#build-and-run-locally-in-a-virtual-environment) - Cost: 0. Doesn't use Azure or Docker Hub.

* [Creating the Python web app to connect to Spotify](#create-the-python-web-app-to-connect-to-spotify) - This discusses how this sample app was created.

* [App Service configuration](#app-service-configuration) - Miscellaneous notes about running in App Service.

## Build in Azure and deploy to App Service with Azure Container Registry

Requirements:

* [Git for Windows](https://git-scm.com/download/win) - if you clone the repo, otherwise you can download it.
* [Spotify API key](https://developer.spotify.com/documentation/web-api/quick-start/)
* [Azure subscription](https://azure.microsoft.com/free/) - if you choose to run in Azure.
* [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) installed locally **OR** you can do everything with the [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/overview) which doesn't require anything installed locally. 

These steps create an Azure Container Registry, build a container image in the registry, and deploy the image to App Service. Registry admin credentials are used by the App Service to pull images. 

What will this cost? We estimate about 5 USD a month, with all the cost being the Azure Container Registry. To reduce that cost to zero, deploy from GitHub or a private registry.

Notes about the steps:

* We show commands with Bash shell. If you are using another type of shell, you're environment variable definitions and command continuations characters will be different. For example, in the Windows command shell set a variable with `SET LOCATION=eastus`, list a variable with `echo %LOCATION%` and the line continuation character is a back tick ("\`"). In PowerShell, set a variable with `$LOCATION='eastus'` and the line continuation character is a back tick ("\`").

* Registry and website names must be unique. You may have to vary the names suggested here with an ending to find unique names. For example, "spotifyplaylist99". (Resources groups, container image, and App Service plan names in a registry don't have to be unique across Azure.)

**Step 1.** Clone this sample repo.

```bash
git clone <this-repo-name>
cd <this-repo-name>
```

You can [fork](https://docs.github.com/get-started/quickstart/fork-a-repo) the repo to your own GitHub account and clone that repo. Or, you can just download the code directly as a zip.

**Step 2.** Create environment variables you'll use in subsequent commands.

Change these variables as appropriate for your situation.

```bash
export RESOURCE_GROUP=myresourcegroup
export LOCATION=eastus
export REGISTRY_NAME=myregistry123abc
export REPO_NAME_AND_TAG=spotifyplaylistpython:latest
export PLAN=myappserviceplan
export SITE_NAME=spotifyplaylist123abc
export CONTAINER_NAME=$REGISTRY_NAME.azurecr.io/$REPO_NAME_AND_TAG
```

**Step 3.** Create a resource group to hold your Azure resources.

```bash
az group create -g $RESOURCE_GROUP -l $LOCATION
```

**Step 4.** Create an Azure Container Registry.

```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic --admin-enabled true
```

**Step 5.** Build the sample code into a container image in Azure (not locally).

```bash
az acr build \
  --image $REPO_NAME_AND_TAG \
  --registry $REGISTRY_NAME .
```

Note the dot (".") at the end of the [az acr build](https://docs.microsoft.com/cli/azure/acr#az-acr-build) command, which means the current directory. Make sure you run the command in the root directory of the project.

Note that you could also use [docker build](https://docs.docker.com/engine/reference/commandline/build/) command and tthe [docker image push](https://docs.docker.com/engine/reference/commandline/image_push/) command to accomplish the same goal, which is to put create and push image to Azure Container Registry. See the section on using Docker Hub to see how this is done.

**Step 6.** Deploy to Azure App Service as a container.

First, create a plan.

```bash
az appservice plan create \
   --resource-group $RESOURCE_GROUP \
   --name $PLAN \
   --is-linux \
   --sku F1
```

Next, create the App Service.

```bash
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN \
  --name $SITE_NAME \
  --deployment-container-image-name $CONTAINER_NAME
```

Keep in mind:

* The registry source is "Azure Container Registry" in your subscription.
* The App Service uses the admin credentials of the Registry to pull the image. A variant below of these steps uses managed identity.
* Check configuration settings with `az webapp config container show -n $SITE_NAME -g $RESOURCE_GROUP`.
* It may take a few moments for the website to build and deploy. Check to the deployment logs to keep an eye on when the site is ready or any problems during the build.

Finally, set the environment variables to pass into the container.

```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $SITE_NAME \
  --settings SPOTIPY_CLIENT_ID=<spotify-client-id> SPOTIPY_CLIENT_SECRET=<spotify-client-secret> DEFAULT_PLAYLIST=5HyEKEpzQU6MxxqeaDIHH3
```

The environment variables passed in our used in the code.

**Step 7.** Browse the website.

For the parameters used above, go to `https://spotifyplaylist123abc.azurewebsites.net`. Change the URL to match your App Service name. The first time the web site comes up it may take some time.

## Build in Azure and deploy to App Service with Managed Identity to Access Azure Container Registry

In this variant of using Azure Container Registry, we use managed identity so that the App Service can pull images from the registry. See the requirements above.

**Steps 1 - 3**, the same as above.

**Step 4.** Create an Azure Container Registry *without* admin enabled.

```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic
```

**Step 5.** same as above.

**Step 6.** Deploy to Azure App Service as a container with managed identity.

We need to do a little more work to set up managed identity, that is, grant the App Service to access to the container registry.

First, we need to get the resource ID of the registry.

```bash
export REGISTRY_RESOURCE_ID=$(az acr show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query id --output tsv)
echo $REGISTRY_RESOURCE_ID
```

Second, use the webapp create command adding scope (using the resource id) and role (acrpull) information.

```bash
az appservice plan create \
  --resource-group $RESOURCE_GROUP \
  --name $PLAN \
  --is-linux --sku F1

az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN \
  --name $SITE_NAME \
  --assign-identity '[system]' \
  --scope $REGISTRY_RESOURCE_ID \
  --role acrpull \
  --deployment-container-image-name $CONTAINER_NAME 
```

Set the App Service to use managed identity for deployment.

```bash
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $SITE_NAME \
  --generic-configurations '{"acrUseManagedIdentityCreds": true}'
```

If you are using Visual Studio, the "Docker Registry: Deploy Image to Azure App Service ..." accomplishes the same type of deployment using managed identity.

Finally, set the environment variables to pass into the container.

```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $SITE_NAME \
  --settings SPOTIPY_CLIENT_ID=<spotify-client-id> SPOTIPY_CLIENT_SECRET=<spotify-client-secret> DEFAULT_PLAYLIST=5HyEKEpzQU6MxxqeaDIHH3
```

## Build and deploy a App Service with Docker Hub

You might choose Docker Hub (personal) over Azure Container Registry to save money hosting the registry.

Requirements:

* [Git for Windows](https://git-scm.com/download/win) - if you clone the repo, otherwise you can download it.
* [Spotify API key](https://developer.spotify.com/documentation/web-api/quick-start/)
* [Azure subscription](https://azure.microsoft.com/free/) - if you choose to run in Azure.
* [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) installed locally **OR** you can do everything with the [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/overview) which doesn't require anything installed locally.
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed locally.
* [Docker Hub](https://hub.docker.com/) account.


**Step 1.** Clone this sample repo.

```bash
git clone <this-repo-name>
cd <this-repo-name>
```

You can [fork](https://docs.github.com/get-started/quickstart/fork-a-repo) the repo to your own GitHub account and clone that repo. Or, you can just download the code directly as a zip.

**Step 2.** Create environment variables we'll use in subsequent commands.

Change these variables as appropriate for your situation. Note that here the container name references Docker Hub user registry and not Azure Container Registry.

```bash
export RESOURCE_GROUP=myresourcegroup
export LOCATION=eastus
export REGISTRY_NAME=<docker-hub-account-name>
export REPO_NAME_AND_TAG=spotifyplaylistpython:latest
export PLAN=myappserviceplan
export SITE_NAME=spotifyplaylist456abc
export CONTAINER_NAME=$REGISTRY_NAME/$REPO_NAME_AND_TAG
```

**Step 3.** Create a resource group to hold your Azure resources.

```bash
az group create -g $RESOURCE_GROUP -l $LOCATION
```

**Step 4.** Create a [Docker Hub](https://hub.docker.com/) account if you don't have one already. 

**Step 5.** Build the sample code into a container image and push to Docker Hub.

```bash
docker build --pull \
  --file "./Dockerfile" \
  --tag "$REGISTRY_NAME/spotifyplaylistpython:latest" . 

docker image push $REGISTRY_NAME/spotifyplaylistpython:latest
```

When the target container registry was Azure Container Registry, we used the [az acr build](https://docs.microsoft.com/cli/azure/acr#az-acr-build) command to build and push into the registry. With Docker Hub, we'll use Docker CLI instead and do it with two separate commands, the [docker build](https://docs.docker.com/engine/reference/commandline/build/) command and the [docker image push](https://docs.docker.com/engine/reference/commandline/image_push/) command. Type `docker` to make sure docker is installed.

**Step 6.** Deploy to Azure App Service as a container coming from a public Docker Hub image. If it's a private image, use a variation of these instructions specifying username and password. See the [az webapp create](https://docs.microsoft.com/cli/azure/webapp#az-webapp-create) command documentation.

First, create a plan.

```bash
az appservice plan create \
   --resource-group $RESOURCE_GROUP \
   --name $PLAN \
   --is-linux \
   --sku F1
```

Next, create the App Service using an image from Docker Hub.

```bash
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN \
  --name $SITE_NAME \
  --deployment-container-image-name $CONTAINER_NAME
```

The command looks identical to the one use for Azure Container Registry. The only part that changes is the `deployment-container-image-name` in that it now points to an image in Docker Hub.

Finally, set the environment variables to pass into the container.

```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $SITE_NAME \
  --settings SPOTIPY_CLIENT_ID=<spotify-client-id> SPOTIPY_CLIENT_SECRET=<spotify-client-secret> DEFAULT_PLAYLIST=5HyEKEpzQU6MxxqeaDIHH3
```

> **Note**
> You could use the `az webapp` commands in the [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/overview) if you don't have Azure CLI installed locally. In this scenario, open a Cloud Shell, set the variables as shown above, and then run the commands as shown.

## Build and run locally in a container

Building locally requires more setup time but is a good investment when you start to modify code and want to test locally before deployment. Or, if you don't want to deploy anything to the cloud and running locally is good enough, then follow these steps. These steps run a container locally. See the next section for using a virtual environment.

Requirements:

* [Git for Windows](https://git-scm.com/download/win) - if you clone the repo, otherwise you can download it.
* [Spotify API key](https://developer.spotify.com/documentation/web-api/quick-start/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) running.

**Step 1.** Get the code.

```bash
git clone <this-repo-name>
cd <this-repo-name>
```

You can [fork](https://docs.github.com/get-started/quickstart/fork-a-repo) the repo to your own GitHub account and clone that repo. Or, you can just download the code directly as a zip.

**Step 2.** Build the image.

You can use the VS Code command palette, the VS Code Docker extension UI, or use Docker commands directly to work with images and containers. Here, we'll show Docker commands assuming you are not using VS Code. Start in the root of the project directory and run this in a Bash shell:

```bash
docker build --pull \
  --file "./Dockerfile" \
  --tag "spotifyplaylistpython:latest" . 
```

Notes:

* Note the dot (".") at the end of the command.  
* Use the `--no-cache` option to force rebuild. (Not shown above.)
* Note that the name of the image comes from the `--tag` option. When building in VS Code from UI, the name used is the project name lower-cased and with no hyphens.
* Change the line continuation characters if you use a shell other than Bash.

After this command runs, you should have a new image in the **IMAGES** part of the Docker extension. 

List images:

```Docker
docker images
```

**Step 3.** Run the container image.

First, create an *.env* file with the following:

```bash
SPOTIPY_CLIENT_ID=<spotify-client-id>
SPOTIPY_CLIENT_SECRET=<spotify-client-secret>
DEFAULT_PLAYLIST=5HyEKEpzQU6MxxqeaDIHH3
FLASK_ENV=development
FLASK_APP=app.py
```

Now, run the image locally using those environment variables:

```bash
docker run -it \
 --env-file .env \
 --publish 5002:5002/tcp spotifyplaylistpython:latest
```

At this point, you have a *.env* file in your project, but it won't be copied into the container because the *.dockerignore* file has a line to ignore *.env*. (So does the *.gitignore* file so that it won't get checked into source.) We use the *.env* file to pass in environment variables to the container on the command line with the `--env-file` option. Environment variables contain keys and secrets needed in the program. We don't want them stored inside the container or in a repo checked in to GitHub.

In Visual Studio Code, you can see the see the running images in the **CONTAINERS** section of the Docker extension. You can also see and work with the container in the Docker Desktop application.

The `-it` runs interactively. You can also run detached. See `docker run --help`.

**Step 4.** Check the running container.

You can execute a command inside a RUNNING container. For example, if you list the environment variables as show with the first command below, you should see the environment variables passed in with the `--env-file` option of the run command.

```bash
docker exec --interactive --tty <friendly-name-of-container> env   
docker exec --interactive --tty <friendly-name-of-container> ls -al
```

**Step 5.** Browse the local site.

Go to [http://127.0.0.1:5002](http://127.0.0.1:5002).

## Build and run locally in a virtual environment

These steps don't require a container and just use a virtual environment. These are probably the simplest way to run the code.

Requirements:

* [Git for Windows](https://git-scm.com/download/win) - if you clone the repo, otherwise you can download it.
* [Spotify API key](https://developer.spotify.com/documentation/web-api/quick-start/)

**Step 1.** Get the code.

```bash
git clone <this-repo-name>
cd <this-repo-name>
```

You can [fork](https://docs.github.com/get-started/quickstart/fork-a-repo) the repo to your own GitHub account and clone that repo. Or, you can just download the code directly as a zip.

**Step 2.** Create a virtual directory.

```bash
python3 -m venv .venv
```

**Step 3.** Activate the virtual environment.

```bash
source .venv/Scripts/activate
```

**Step 4.** Install requirements.

```bash
pip install -r requirements.txt
```

**Step 5.** Create an *.env* file based on the *.env.example* file.

```
SPOTIPY_CLIENT_ID=<spotify-client-id>
SPOTIPY_CLIENT_SECRET=<spotify-client-secret>
DEFAULT_PLAYLIST=6rY4wDAA1Ueai9xSPFXCpa
FLASK_ENV=development
FLASK_APP=app.py
```

Fil in the `\<spotify-client-id>` and `\<spotify-client-secret>` with your values.

**Step 6.** Start the server.

```bash
flask run
```

**Step 7.** Browse the local site.

Go to [http://127.0.0.1:5000](http://127.0.0.1:5000).


## Create the Python web app to connect to Spotify

This section is for those interested in how we developed the code in this repo. This is not the only way to do, rather how we approached it.

We'll bootstrap the process of installation using a virtual environment. If you plan to run locally only with containers, the virtual environment won't be used. However, we find that when working with Python and containers, we often make make sure the code works both in a virtual environment and running in a container. The iteration cycle of code-test-fix is slightly quicker in virtual environment.

We follow a combination of these [instructions](https://realpython.com/django-setup/) as well as these for [Flask installation](https://flask.palletsprojects.com/en/2.1.x/installation/). These instructions were tested on Windows with Visual Studio Code.

```bash
mkdir spotifyplaylist-python
cd spotifyplaylist-python
py -3.9 -m venv .venv
source .venv/Scripts/activate
pip install Flask
```

We'll call the virtual environment *.venv* so that later the *dockerignore* will exclude this folder when copying files to the container. It's a default exclusion rule in the *dockerignore* file.

Create a basic *app.py* to test everything:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
```

Starting in the root of the project, run this simple app in the virtual environment with:

```bash
flask run
```

As a shortcut, if the file is named *app.py* or *wsgi.py*, you don’t have to set the `FLASK_APP` environment variable. If our application were instead named *hello.py* we would run it like so:

```bash
export FLASK_APP=hello
flask run
```

In bash, set an environment variable like so `FLASK_APP=hello`. To enable all development features, set the `FLASK_ENV` to `development` before running.

### Generate a secret key

Generate a [secret key](https://flask.palletsprojects.com/en/2.1.x/config/#SECRET_KEY) unique to project that will be used to sign session cookies. The value that the command below produces is used in the *production.py* file.

```python
python -c "import secrets; print(secrets.token_hex())"
```

The value should look similar to this "612f971dc0c036d8dd332f15822e1eb9c03891fd4fe6a905446679ddeeb34318".

### Create project files

Create in order:

* *.gitignore* file
* *.env* file
* *requirements.txt* file
* *project* folder that contains *development.py* and *production.py*
* *static* folder that contains *favicon.ico* and *spotifyplaylist.css*
* *templates* folder that contains *\*.html* template files.

Create a *base.html* template file that contains Bootstrap references and links to *favicon.ico* and *spotifyplaylist.css*. Then create an *index.html* file extending the *base.html* to be the main landing page. Change the index method in *app.py* to point to template.

```python
@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')
```

At this point, we continued to build out the functionality as it exists in the current code repository. All along, we are testing in the virtual environment as so:

```bash
export SPOTIPY_CLIENT_ID=<your-client-id>
export SPOTIPY_CLIENT_SECRET=<your-client-secret>
export DEFAULT_PLAYLIST=5HyEKEpzQU6MxxqeaDIHH3
export FLASK_ENV=development
export FLASK_APP=app.py

flask run
```

### Set up project for containerization with Docker

#### Install required components

Install the [Docker extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) for Visual Studio Code. You must have [Docker](https://docs.docker.com/get-docker/) on your machine as well.

If you haven't done so already, create a [Docker Hub](https://hub.docker.com/repositories) repository. Using a personal account option should be enough for this tutorial and will not incur any costs. You can also use Azure Container Registry.

#### Add Docker files to the project and push image to a registry

You can do this with Visual Studio Code extension task "Docker: Add Docker files to Workspace". 

1. Use **F1** or **SHIFT** + **CTRL** + **P** to bring up the command palette and search for the task "Docker: Add Docker files to Workspace". 
1. Select *Python: Flask* for application platform.
1. Select *app.py* for entry point.
1. Select *5002* for port the app listens on.
1. Select *Yes* for include optional Docker Compose files.

The task adds the following files to the project:

* *Dockerfile* - Used when running the `docker build` command.
* *.dockerignore* - Contains rules excluding what gets copied to the container during build.
* *docker-compose.yml* - Used when running the `docker compose` command.
* *docker-compose.debug.yml* - Debug version of compose.

The steps to build and run locally are covered in the [section above](#build-and-run-locally-and-optionally-deploy-to-app-service). The only difference with previous command is that to use the Docker CLI push command you need to have the image name fully qualified.

To see how to create and push a container image to Azure Container Registry, see [Build in Azure and Deploy to App Service](#build-in-azure-and-deploy-to-app-service-with-azure-container-registry).

To see how to create and push a container image to Docker Hub, see [Build and deploy to App Service with Docker Hub.](#build-and-deploy-to-app-service-with-docker-hub)

If you are using VS Code, Make sure you are logged into Azure in the **REGISTRIES** section of the Docker extension.

With Azure Container Registry and using Docker CLI push command, you might need to enable ACR Admin user. For more information, see [Authentication Overview](https://docs.microsoft.com/azure/container-registry/container-registry-authentication) for Azure Container Registry.

First, try `docker login` and see if that gives you the permission you need, authorizing with existing credentials. If not, specify username and password with the command:

```dockerfile
docker login $REGISTRY_NAME.azurecr.io
```

Connected to Azure Container Registry, you are ready to push to the registry, for example.

```bash
docker push $REGISTRY_NAME.azurecr.io/spotifyplaylistpython:latest
```

## App Service configuration

In App Service, you specify environment variables with configuration settings. (When running locally, the environment variables can be specified with an *.env* file, which isn't used in production.) 

The values are configuration settings of the App Service that are common to all scenarios are:

* SPOTIPY_CLIENT_ID=\<client-id>
* SPOTIPY_CLIENT_SECRET=\<client-secret>
* DEFAULT_PLAYLIST="5HyEKEpzQU6MxxqeaDIHH3"

Other configuration settings depend on where the container is pulled from. For containers pulled from Azure Container Registry:

* DOCKER_REGISTRY_SERVER_URL=\<azure-container-registry-name>.azurecr.io
* DOCKER_REGISTRY_SERVER_USERNAME=\<azure-container-registry-admin-user-name>
* DOCKER_REGISTRY_SERVER_PASSWORD=\<azure-container-registry-password>

For containers pulled from Docker Hub:

* DOCKER_REGISTRY_SERVER_URL=<docker-hub-account-name>
