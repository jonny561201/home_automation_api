#!/usr/bin/env bash


HOME_AUTO_SERVICE_FILE=homeAutomation.service


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
copyServiceFile
configureSystemD
restartDevice