#!/usr/bin/env bash

YELLOW='\033[1;33m'
WHITE='\033[0m'
RED='\033[0;31m'

HOME_AUTO_SERVICE_FILE=homeAutomation.service


function cloneServiceFiles {
    if [[ -d "/home/pi/home_automation_api" ]]; then
        echo -e "${YELLOW}---------------Service Folder Exists---------------${WHITE}"
        cd /home/pi/home_automation_api
        git pull
    else
        echo -e "${YELLOW}---------------Cloning Service---------------${WHITE}"
        cd /home/pi/
        git clone https://github.com/jonny561201/home_automation_api.git /home/pi/home_automation_api
    fi
}

function startVirtualEnv {
    if [[ ! -d "/home/pi/home_automation_api/venv" ]]; then
      echo -e "${YELLOW}----------Creating VirtualEnv----------${WHITE}"
      pushd "/home/pi/home_automation_api"
      pip3 install virtualenv
      python3 -m virtualenv venv
      popd
    fi
      echo -e "${YELLOW}---------------starting VirtualEnv---------------${WHITE}"
      source ./venv/bin/activate
}

function installDependencies {
    echo -e "${YELLOW}---------------Installing Dependencies---------------${WHITE}"
    pip3 install -Ur requirements.txt
}

function stopService {
    echo -e "${YELLOW}---------------Stopping Service---------------${WHITE}"
    sudo systemctl stop ${HOME_AUTO_SERVICE_FILE}
    sudo rm /lib/systemd/system/${HOME_AUTO_SERVICE_FILE}
}

function copyServiceFile {
    echo  -e "${YELLOW}---------------Creating SystemD---------------${WHITE}"
    sudo chmod 666 ${HOME_AUTO_SERVICE_FILE}
    sudo yes | sudo cp ./deployment/${HOME_AUTO_SERVICE_FILE} /lib/systemd/system/${HOME_AUTO_SERVICE_FILE}
}

function configureSystemD {
    echo  -e "${YELLOW}---------------Configuring SystemD---------------${WHITE}"
    sudo systemctl daemon-reload
    sudo systemctl enable ${HOME_AUTO_SERVICE_FILE}
}

function migrateDatabase {
    echo  -e "${YELLOW}---------------Migrating Database---------------${WHITE}"
    python3 -m yoyo apply -b --database postgresql://${SQL_USERNAME}:${SQL_PASSWORD}@localhost:${SQL_PORT}/${SQL_DBNAME} ./docker/flyway/migration/
}

function restartDevice {
    echo  -e "${YELLOW}---------------Rebooting Device---------------${WHITE}"
    sudo reboot
}

function createEnvironmentVariableFile {
    if [[ ! -f "/home/pi/home_automation_api/serviceEnvVariables" ]]; then
        echo -e "${YELLOW}---------------Creating Environment Variable File---------------${WHITE}"
        createFile
    else
        echo -e "${YELLOW}---------------Environment Variable File Already Exists---------------${WHITE}"
        echo 'Would you like to recreate serviceEnvVariables file? (y/n)'
        read USER_RESPONSE
        if [[ ${USER_RESPONSE} == "y" ]]; then
            createFile
        fi
    fi
    echo -e "${YELLOW}---------------Exporting Environment Variables---------------${WHITE}"
    set -o allexport; source ./serviceEnvVariables; set +o allexport
}

function createFile {
    echo -e "Enter JWT_SECRET:${WHITE}"
    read JWT_SECRET
    echo -e "Enter SQL_USERNAME:${WHITE}"
    read SQL_USER
    echo -e "Enter SQL_PASSWORD:${WHITE}"
    read SQL_PASS
    echo -e "Enter LIGHT_API_KEY:${WHITE}"
    read LIGHT_API_KEY
    echo -e "Enter WEATHER_APP_ID:${WHITE}"
    read WEATHER_APP

    echo "PYTHON_ENVIRONMENT=production" > serviceEnvVariables
    echo "JWT_SECRET=${JWT_SECRET}" >> serviceEnvVariables
    echo "SQL_USERNAME=${SQL_USER}" >> serviceEnvVariables
    echo "SQL_PASSWORD=${SQL_PASS}" >> serviceEnvVariables
    echo "LIGHT_API_KEY=${LIGHT_API_KEY}" >> serviceEnvVariables
    echo "WEATHER_APP_ID=${WEATHER_APP}" >> serviceEnvVariables
}


stopService
cloneServiceFiles
startVirtualEnv
installDependencies
createEnvironmentVariableFile
migrateDatabase
copyServiceFile
configureSystemD
restartDevice