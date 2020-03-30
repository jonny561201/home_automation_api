# Project Purpose #
- Create flask APis for a whole home automation webpage
- Maintain security through login and persistence of JWT tokens
- Learn more about application hosting on Raspberry Pi

# Deployment #
1. Copy startService.sh to `/home/pi/` directory
    * execute `chmod +x startService.sh` to make it executable
2. Create file `/home/pi/serviceEnvVariables` and list all environment variables
3. Execute `startService.sh` file to create service
    * stops service if it is running
    * clones repo down if doesnt initially exist
    * does a pip install of all production dependencies
    * uses `yoyo-migrations` from python to migrate the production database
    * copies `homeAutomation.service` file into systemd
    * registers and configures service
    * reboots the device
    * application will run on boot and pull in environment variables to file


# Development #
1. After cloning repo:
    * create virtual environment: `virtualenv venv`
    * activate virtual environment: `source ./venv/scripts/activate`
    * install production dependencies: `pip install -Ur requirements.txt`
    * install test dependencies: `pip install -Ur test_requirements.txt`
2. Install docker desktop for linux containers
3. Provide any corresponding test coverage in directories `/test/integration` and `/test/unit`
4. Prior to committing code execute `./run_all_tests.sh`
    * will start/stop a postgres docker container
    * will execute flyway against postgres database
5. Stand up application by executing `python app.py`

