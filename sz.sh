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

case $1 in
    start)
        docker-compose up -d
        ;;
    stop)
        docker-compose down
        ;;
    install)
        installFunc
        ;;
    update)
        echo "Update is currently not supported"
        ;;
    *)
        echo "Usage: sz.sh [start|stop|install|update]"
        exit 1
        ;;
esac