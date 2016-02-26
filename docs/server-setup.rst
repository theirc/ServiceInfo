Server Setup
========================


Provisioning
------------------------

The server provisioning is managed using `Salt Stack <http://saltstack.com/>`_. The base
states are managed in a `common repo <https://github.com/caktus/margarita>`_ and additional
states specific to this project are contained within the ``conf`` directory at the root
of the repository.

For more information see the doc:`provisioning guide </provisioning>`.


Layout
------------------------

Below is the server layout created by this provisioning process::

    /var/www/service_info/
        source/
        env/
        log/
        public/
            static/
            media/
        ssl/

``source`` contains the source code of the project. ``env``
is the `virtualenv <http://www.virtualenv.org/>`_ for Python requirements. ``log``
stores the Nginx, Gunicorn and other logs used by the project. ``public``
holds the static resources (css/js) for the project and the uploaded user media.
``public/static/`` and ``public/media/`` map to the ``STATIC_ROOT`` and
``MEDIA_ROOT`` settings. ``ssl`` contains the SSL key and certificate pair.


Deployment
------------------------

For deployment, each developer connects to the Salt master as their own user. Each developer
has SSH access via their public key. These users are created/managed by the Salt
provisioning. The deployment itself is automated with `Fabric <http://docs.fabfile.org/>`_.
To deploy, a developer simply runs::

    # Deploy updates to staging
    fab staging deploy
    # Deploy updates to production
    fab production deploy

This runs the Salt highstate for the given environment. This handles both the configuration
of the server as well as updating the latest source code. This can take a few minutes and
does not produce any output while it is running. Once it has finished the output should be
checked for errors.


New server on AWS
-----------------

#. Create a new EC2 server. Some tips:

 * Put it in a region close to where most users will be, e.g. Ireland (eu-west-1).
   (To switch regions in the AWS EC2 console, look near the top-right of the window for
   a light-gray selector on a black background.)
 * Use an AMI (image) of Ubuntu 14.04 server, 64-bit, EBS - e.g. ubuntu-trusty-14.04-amd64-server-20140927 (ami-b83c0aa5)
 * Be sure to save the private key that is created, or use
   an existing one you already own. (Caktus: key pairs are stored
   in LastPass, search for CTS.) The AWS private key is only
   needed until CTS has been deployed the first time, but it
   is essential until then.

#. If needed, add a new environment in the fabfile and Salt config files.

#. Add the new server's ssh key to your ssh-agent, e.g.::

    ssh-add /path/to/newserver.pem

   This will allow you to ssh into the new server as ``ubuntu`` initially.
   After we've finished our deploy, you'll have your own userid on
   the server that you can use to ssh in.

#. Create a master::

    fab -u ubuntu staging setup_master

#. Create a minion and assign initial roles::

    fab -u ubuntu staging setup_minion:balancer,queue,cache,web,worker,beat

#. Initial deploy::

    fab -u ubuntu staging deploy

After that, developer accounts will exist on the server with ssh access,
so "-u ubuntu" will no longer be needed.  You'll be able to update
the server with::

  fab staging deploy
