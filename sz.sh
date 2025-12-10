#!/usr/bin/bash
#
# sz helper script to start/stop the sz
#
p=`dirname $0`
DIR=`realpath $p`
cd $DIR

function installFunc {
    cat sz.service | \
    sed s:LOCAL_SZ_INSTALLATION_SOURCE:$DIR: \
    > /etc/systemd/system/sz.service
    systemctl daemon-reload
    systemctl enable sz.service
    systemctl start sz.service
}

function updateFunc {
    git pull
    git clone https://huggingface.co/datasets/fmoorhof/selectzyme-app-data data
    docker build -t ipb-halle/selectzyme-app:development .
}

case $1 in
    start)
        docker-compose up -d
        ;;
    stop)
        docker-compose down
        ;;
    restart)
        docker-compose restart
        ;;
    install)
        installFunc
        ;;
    update)
        updateFunc
        ;;
    *)
        echo "Usage: sz.sh [start|stop|install|update]"
        exit 1
        ;;
esac
