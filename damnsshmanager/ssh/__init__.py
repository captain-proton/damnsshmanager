from damnsshmanager.ssh.native import NativeConnector
from damnsshmanager.ssh.paramiko import ParamikoConnector

ssh_connectors = {
    'system': NativeConnector,
    'application': ParamikoConnector
}
