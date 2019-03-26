********************
The damn ssh manager
********************

Why?
====

It looks like, that it is really hard to find a ssh connection managing instance that just saves ssh connection details through an alias. I am not able to remember all the hosts that I am responsible for, therefore a manager is needed. One may say ... "Dude, do this shit in (ba)sh! ... stupid". But for me shell scripting is, in most of the cases, just an annoying task.

So there it is. A python script that stores ssh connection details. You can even run ssh connections and local tunnels with it ... hell yeah! It is all based on a single small file in your home directory called ``hosts.pickle`` and ``localtunnels.pickle`` under the directory ``damnsshmanager``. One host contains simply the attributes as does the tunnels.

- ``alias``
- ``addr``
- ``port``
- ``username``

Local tunnels are based on saved hosts! No hosts means no local tunnels, so just create one.

- ``alias``
- ``gateway``
- ``remote port``
- ``local port``
- ``destination``

This way you don't have to specify multiple host connections for every new tunnel. The gateway is equal to the alias used to define the host connection.

Example:

.. code-block:: shell

    dsm add foo some.strange.host -u hero
    dsm ltun --destination example.com bar foo 80
    dsm c bar

The first command creates a connection to the strange host. The second one adds a tunnel that runs on example.com to the remote port 80 of the strange host. A local port is, if not specified, automatically chosen by the manager. The last command opens the tunnel. On normal ssh this would mean ``ssh -L 49152:example.com:80 hero@some.strange.host``. Local port range is from 49152 til 65535.

There is a `great description <https://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html>`_ on how ssh tunnels work.

At the moment this thing handles no more data! It is *developed* just for this simple reason.

Installation
============

via pip
-------

.. code-block:: shell

    pip install damnsshmanager

from sources
------------

.. code-block:: shell

    git clone https://github.com/captain-proton/damnsshmanager

    cd damnsshmanager

    python3 setup.py install

Usage
=====

With the installation comes the script ``dsm``.

.. code-block:: shell

    dsm -h

+---------+--------------------------------------------------------------------------+
| Action  |                                 Command                                  |
+=========+==========================================================================+
| add     | ``dsm add <alias> <hostname> [-u username] [-p port]``                   |
+---------+--------------------------------------------------------------------------+
| ltun    | ``dsm ltun <alias> <gateway> <remote port> [local_port] [destionation]`` |
+---------+--------------------------------------------------------------------------+
| delete  | dsm del <alias>                                                          |
+---------+--------------------------------------------------------------------------+
| connect | dsm c <alias>                                                            |
+---------+--------------------------------------------------------------------------+


When run without parameters all saved instances are tested.

.. image:: hosts.png
