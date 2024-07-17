# Deploying to Azure

This page explains how to migrate all the code into a virtual environment in Azure to then schedule a mensual scraping task. It will explain all the steps to go from the button into an automated script.

Index:
- [Code Changes](#coding-layout)  
- [Steps for deployment](#steps-to-deploy-to-azure)


## Code Changes

An example of all the code is available in the repository under:

```cmd
.\MI_Simon\my-web-scraper
```

The following files are different from the original code:
- [main.py](#mainpy)
- [scrapers.py](#scraperspy)
- [SupportFunctions.py](#supportfunctionspy)
- [Dockerfile](#dockerfile)


### main.py
The main script is completely different from the original script. Firstly, the 'tkinter' module is not used anymore as an interface will not be required for the automation. The multithreading has also been removed as speed is not an issue as the code will be running overnight on the first day of the month. For a more detailed breakdown of the code, have a look at the file path:
```cmd
.\MI_Simon\my-web-scraper\main.py
```

### scrapers.py
There aren't a lot of changes in the scrapers.py functions, but due to the nature of the container the selenium scrapes had to be changed. Below are some of the changes needed:

```python
# New modules

from webdriver_manager.chrome import ChromeDriverManager 
        # This downloads the chrome driver to be used by the container
```

```python
# Before:
def selenium_scrape(url : str) -> BeautifulSoup:
    '''For given URL open page and fetch content.
    
    :Params:
        url (str): Url for site to scrape
    
    :Returns:
        BeautifulSoup object containing website HTML
    '''
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages
    driver=webdriver.Chrome(options=options)
    driver.get(url=url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    driver.close()
    
    return soup

# After:
def selenium_scrape(url : str) -> BeautifulSoup:
    '''For given URL open page and fetch content.
    
    :Params:
        url (str): Url for site to scrape
    
    :Returns:
        BeautifulSoup object containing website HTML
    '''
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('log-level=3')  # Suppress console messages

    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    driver.get(url=url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    driver.close()
    
    return soup

# Explanation:
#   More options have to be added to the selenium webdriver as otherwise it won't work as a containarised app. The most important options are
#       - options.add_argument('--headless') - this options doesn't work for a few companies, look in the code for more details.
#       - options.add_argument('--disable-gpu')

```
### SupportFunctions.py
Since this script must now upload all the data into Azure blob storage, there are new functions stored in this script which is used in main.py. The credentials have been added into the script (which will be moved to an encrypted file later) and all of the functions have been changed so it can read/write/reallocate accordingly in blob storage.

### Dockerfile
The Dockerfile is required as the script is firstly transformed into a containerised application within docker and tested locally to then be migrated into **Azure Container Registry (ACR)**. This dockerfile is different from the usual as it uses 'xvbd' which allows the virtual environment to use a 'virtual' screen to open selenium in a __'no headless'__ mode as this is required for some of the websites. The docker file also installs the necessary dependencies for the container to work appropriately, such as a stable version of Google Chrome for the selenium modules to work. For more details on the docker file, access it via:

```cmd
.\MI_Simon\my-web-scraper\Dockerfile
```

### manifest.yaml

This is a configuration used to migrate the docker image to ACR when necessary. It is very default, and the only variable changed was the name of the application to **kubrickmiproject**. The file can be found in the same directory as the other scripts.


## Steps to deploy to Azure

Follow these steps to deploy your Docker image to Azure and schedule it to run every first day of the month at 00:00 using Azure Logic Apps.

### 1. Build, Test, and Push Docker Image to Azure Container Registry (ACR)

1. **Login to Azure CLI:**
    ```sh
    az login
    ```

2. **Create an Azure Container Registry (ACR):**
    ```sh
    az acr create --resource-group <resource_group_name> --name <acr_name> --sku Basic
    ```

3. **Login to ACR:**
    ```sh
    az acr login --name <acr_name>
    ```

4. **Build your Docker image locally:**
    ```sh
    docker build -t <local_image_name> .
    ```

5. **Test your Docker image locally:**
    ```sh
    docker run -it --rm <local_image_name>
    ```

    Ensure that your container runs as expected.

6. **Tag the Docker image for ACR:**
    ```sh
    docker tag <local_image_name> <acr_name>.azurecr.io/<repository_name>:<tag>
    ```

7. **Push the Docker image to ACR:**
    ```sh
    docker push <acr_name>.azurecr.io/<repository_name>:<tag>
    ```

### 2. Test the Container in ACR

1. Login to [Azure Portal](https://portal.azure.com) and navigate to ACR to then test whether the container runs correctly

2. This can be verified by checking the logs of the container and also checking the log files/data in the blbo stoage


### 3. Create an Azure Logic App to Schedule the Container

1. **Go to Azure Portal:**
    - Navigate to [Azure Portal](https://portal.azure.com).

2. **Create a new Logic App:**
    - Search for "Logic Apps" in the search bar and select "Create".
    - Fill in the required details like resource group, name, and region.
    - Click "Review + create", then "Create".

3. **Configure the Recurrence Trigger:**
    - Open your new Logic App.
    - In the Logic App Designer, search for "Recurrence" and select the trigger.
    - Set the recurrence settings to trigger monthly on the 1st day at 00:00 (UTC).

    Example settings:
    - **Frequency**: Month
    - **Interval**: 1
    - **At these minutes**: 0
    - **At these hours**: 0
    - **On these days**: 1

4. **Add an Action to Create an Azure Container Instance (ACI):**
    - Click "New step", search for "Azure Container Instances", and select it.
    - Choose the "Create or update container group" action.

5. **Configure the Action:**
    - Fill in the necessary details such as resource group, container group name, and container details.
    - Set the container image to the one you pushed to ACR (e.g., `<acr_name>.azurecr.io/<repository_name>:<tag>`).
    - Provide the registry login server, username, and password.
    - Example:
        - **Resource Group**: `<resource_group_name>`
        - **Container Group Name**: `<container_group_name>`
        - **Image**: `<acr_name>.azurecr.io/<repository_name>:<tag>`
        - **CPU Cores**: 1
        - **Memory (GB)**: 1.5
        - **Registry Login Server**: `<acr_name>.azurecr.io`
        - **Registry Username**: `<acr_username>`
        - **Registry Password**: `<acr_password>`

6. **Save and Enable the Logic App:**
    - Save the Logic App.
    - It will now run the specified ACI on the first day of every month at 00:00 (UTC).
