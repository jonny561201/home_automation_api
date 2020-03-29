#!/usr/bin/env bash

HOME_AUTO_SERVICE_FILE=homeAutomation.service
YELLOW='\033[1;33m'
WHITE='\033[0m'

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


stopService
cloneServiceFiles
installDependencies
copyServiceFile
configureSystemD
restartDevice