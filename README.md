# Project Purpose #
- Create flask APis for a whole home automation webpage
- Maintain security through login and persistence of JWT tokens
- Learn more about application hosting on Raspberry Pi

# Deployment #
1. Copy startService.sh to `/home/pi/` directory
    * execute `chmod +x startService.sh` to make it executable
2. Execute `startService.sh` file to create service
    * stops service if it is running
    * clones repo down if doesnt initially exist
    * does a pip install of all production dependencies
    * creates environment variable file `/home/pi/home_automation_api/serviceEnvVariables`
    * uses `yoyo-migrations` from python to migrate the production database
    * copies `homeAutomation.service` file into systemd
    * registers and configures service
    * reboots the device
    * application will run on boot and pull in environment variables file


# Development #
1. After cloning repo:
    * create virtual environment: `virtualenv venv`
    * activate virtual environment: `source ./venv/scripts/activate`
    * install production dependencies: `pip install -Ur requirements.txt`
    * install test dependencies: `pip install -Ur requirements_test.txt`
2. Install docker desktop for linux containers
3. Create `settings.local.json` file to create local test values for keys
    * `Environment` flag to know what environment you are in based on PYTHON_ENVIRONMENT env var
    * `LightApiKey` api key for the lights microservice
    * `WeatherAppId` app id for the weather provider
    * `JwtSecret` jwt secret for encoding/decoding jwts
    * `EmailAppId` app id for the email provider
    * `TempFileName` filename used to persist desired temperature state
    * `Database` object to be created for persistent storage
      * `Port` database port
      * `Name` database name
      * `User` database username
      * `Password` database password
    * `Queue` object to be created for rabbitmq connection
      * `Host` rabbitmq host
      * `VHost` rabbitmq vhost
      * `Port` rabbitmq port
      * `User` rabbitmq username
      * `Password` rabbitmq password
      * `Exchange` rabbitmq exchange name
    * `BaseUrls` object with external service base urls
      * `Lights` lights microservice url
      * `Weather` weather api url
      * `Email` email api url
    * `Authority` Auth0 configuration
      * `Domain` Auth0 tenant domain
      * `Audience` Auth0 audience
      * `ClientId` Auth0 client id
      * `ClientSecret` Auth0 client secret
4. Provide any corresponding test coverage in directories `/test/integration` and `/test/unit`
5. Prior to committing code execute `./run_all_tests.sh`
    * will start/stop a postgres docker container
    * will execute flyway against postgres database
6. Stand up application by executing `python app.py`
   * For local development use `python local_app.py` as you cannot install GPI library on non-raspberry pi devices
