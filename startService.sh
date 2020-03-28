#!/usr/bin/env bash


HOME_AUTO_SERVICE_FILE=homeAutomation.service


function cloneServiceFiles {
    if [[ -d "/home/pi/GarageDoorApi" ]]
    then
        echo "Directory exists."
        cd /home/pi/GarageDoorApi
        git pull
    else
        echo "Directory does not exist."
        cd /home/pi/
        git clone https://github.com/jonny561201/GarageDoorApi.git
    fi

}

function installDependencies {
    pip3 install -Ur requirements.txt
}

function stopService {
    sudo systemctl stop ${HOME_AUTO_SERVICE_FILE}
}

function copyServiceFile {
    sudo chmod 644 ${HOME_AUTO_SERVICE_FILE}
    sudo yes | cp ${HOME_AUTO_SERVICE_FILE} /etc/systemd/system/${HOME_AUTO_SERVICE_FILE}
}

function configureSystemD {
    sudo systemctl daemon-reload
    sudo systemctl enable ${HOME_AUTO_SERVICE_FILE}
}

function restartDevice {
    sudo reboot
}


stopService
cloneServiceFiles
installDependencies
copyServiceFile
configureSystemD
restartDevice