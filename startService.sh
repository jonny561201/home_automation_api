#!/usr/bin/env bash

YELLOW='\033[1;33m'
WHITE='\033[0m'
RED='\033[0;31m'

HOME_AUTO_SERVICE_FILE=homeAutomation.service
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function cloneServiceFiles {
    if [[ -d "/home/pi/home_automation_api" ]]; then
        echo -e "${YELLOW}---------------Service Folder Exists---------------${WHITE}"
        cd /home/pi/home_automation_api
        git pull
    else
        echo -e "${YELLOW}---------------Cloning Service---------------${WHITE}"
        cd /home/pi/
        git https://github.com/jonny561201/home_automation_api.git
    fi

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
    sudo chmod 644 ${HOME_AUTO_SERVICE_FILE}
    sudo yes | sudo cp ${HOME_AUTO_SERVICE_FILE} /lib/systemd/system/${HOME_AUTO_SERVICE_FILE}
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

        echo -e "Enter SQL_USERNAME:${WHITE}"
        read SQL_USER
        echo -e "Enter SQL_PASSWORD:${WHITE}"
        read SQL_PASS

        echo "SQL_USERNAME=${SQL_USER}" >> serviceEnvVariables
        echo "SQL_PASSWORD=${SQL_PASS}" >> serviceEnvVariables
    else
        echo -e "${YELLOW}---------------Environment Variable File Already Exists---------------${WHITE}"
    fi
}


stopService
cloneServiceFiles
installDependencies
migrateDatabase
copyServiceFile
configureSystemD
createEnvironmentVariableFile
restartDevice