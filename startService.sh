#!/usr/bin/env bash

YELLOW='\033[1;33m'
WHITE='\033[0m'
RED='\033[0;31m'

HOME_AUTO_SERVICE_FILE=homeAutomation.service
SQL_PORT=5432
SQL_PASS=password
SQL_USER=postgres
DB_NAME=garage_door
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function cloneServiceFiles {
    if [[ -d "/home/pi/home_automation_api" ]]
    then
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

function restartDevice {
    echo  -e "${YELLOW}---------------Rebooting Device---------------${WHITE}"
    sudo reboot
}

function validateDockerInstalled {
    if [[ -x "$(command -v docker)" ]]; then
        echo -e "${YELLOW}---------------Docker Installed---------------${WHITE}"
        # command
    else
        echo -e "${RED}---------------Docker Not Installed---------------${WHITE}"
        installDocker
    fi
}

function installDocker {
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
}

function dockerFlywayMigration {
    DOCKER_VOLUME=${SCRIPT_DIR}/docker/flyway/migration
    echo -e "${YELLOW}----------Flyway Volume set to: $DOCKER_VOLUME${WHITE}"
    echo -e "${YELLOW}----------Executing Flyway Migrations----------${WHITE}"
    sudo docker run --net=host --rm -v /${DOCKER_VOLUME}:/flyway/sql boxfuse/flyway:5.2.4 -url="jdbc:postgresql://localhost:$SQL_PORT/$DB_NAME" -user=${SQL_USER} -password=${SQL_PASS} migrate
}

validateDockerInstalled
stopService
cloneServiceFiles
installDependencies
dockerFlywayMigration
copyServiceFile
configureSystemD
restartDevice