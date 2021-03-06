from fabric.api import *
from fabric.contrib.files import exists
import os

SENSUVERSION = "0.26"

@task
def installRabbitMQ():
    run("sudo apt-get update")
    run("sudo apt-get --force-yes -y upgrade")
    sudo('echo "deb http://www.rabbitmq.com/debian/ testing main" | tee -a /etc/apt/sources.list.d/rabbitmq.list')
    sudo("curl -L -o ~/rabbitmq-signing-key-public.asc http://www.rabbitmq.com/rabbitmq-signing-key-public.asc")
    run("sudo apt-key add ~/rabbitmq-signing-key-public.asc")
    run("sudo apt-get update")
    run("sudo apt-get -y upgrade")
    run("sudo apt-get install -y rabbitmq-server erlang-nox --force-yes")
    run("sudo service rabbitmq-server start")
    run("cd /tmp && wget http://sensuapp.org/docs/"+ SENSUVERSION +"/tools/ssl_certs.tar && tar -xvf ssl_certs.tar")
    run("cd /tmp/ssl_certs && ./ssl_certs.sh generate")
    sudo("mkdir -p /etc/rabbitmq/ssl && cp /tmp/ssl_certs/sensu_ca/cacert.pem /tmp/ssl_certs/server/cert.pem /tmp/ssl_certs/server/key.pem /etc/rabbitmq/ssl")
    put("./rabbitmq.config", "/etc/rabbitmq/rabbitmq.config",use_sudo=True)
    run("sudo service rabbitmq-server restart")
    sudo("rabbitmqctl add_vhost /sensu")
    sudo("rabbitmqctl add_user sensu QfP8myKrIS")
    sudo('rabbitmqctl set_permissions -p /sensu sensu ".*" ".*" ".*"')

@task
def installRedis():
    run("sudo apt-get update")
    run("sudo apt-get -y install redis-server --force-yes")

@task
def installSensu():
    sudo("wget -q http://repos.sensuapp.org/apt/pubkey.gpg -O- |  apt-key add -")
    sudo('echo "deb http://repos.sensuapp.org/apt sensu main" |  tee -a /etc/apt/sources.list.d/sensu.list')
    run("sudo apt-get update")
    run("sudo apt-get install -y sensu uchiwa --force-yes")
    sudo('mkdir -p /etc/sensu/ssl')
    sudo('cp /tmp/ssl_certs/client/cert.pem /tmp/ssl_certs/client/key.pem /etc/sensu/ssl')

@task
def configureSensu():
    put("./rabbitmq.json", "/etc/sensu/rabbitmq.json", use_sudo=True)
    put("./redis.json","/etc/sensu/redis.json", use_sudo=True)
    put("./api.json", "/etc/sensu/api.json", use_sudo=True)
    put("./uchiwa.json", "/etc/sensu/uchiwa.json", use_sudo=True)
    put("./client.json", "/etc/sensu/conf.d/client.json", use_sudo=True)
    sudo("update-rc.d sensu-server defaults")
    sudo("update-rc.d sensu-client defaults")
    sudo("update-rc.d sensu-api defaults")
    sudo("update-rc.d uchiwa defaults")

@task
def ufwEnable():
    sudo('ufw --force reset')
    sudo('ufw allow 22/tcp')
    sudo('ufw allow 3000/tcp')
    sudo('ufw default deny')
    sudo('ufw --force enable')

@task
def ufwStatus():
    sudo("ufw status numbered")

@task
def sensuStart():
    run("sudo service sensu-server start")
    run("sudo service sensu-client start")
    run("sudo service sensu-api start")
    run("sudo service uchiwa start")


@task
def sensuStop():
    run("sudo service sensu-server stop")
    run("sudo service sensu-client stop")
    run("sudo service sensu-api stop")
    run("sudo service uchiwa stop")

@task
def sensuStatus():
    run("sudo service sensu-server status")
    run("sudo service sensu-client status")
    run("sudo service sensu-api status")
    run("sudo service uchiwa status")

@task
def sensuRestart():
    sensuStop()
    sensuStart()
    sensuStatus()
    

@task
def CREATEUSER(customUser):
    addCustomUser(customUser)
    setupSSH4User(customUser)
    addSudo()
    lockRoot()

@task
def INSTALL():
    installRabbitMQ()
    installRedis()
    installSensu()
    configureSensu()
    ufwEnable()
    sensuStart()
    sensuStatus()





