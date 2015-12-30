Development Setup
=================


.. _clone-the-repository:

Clone the Repository
--------------------

To get started, you'll first need to clone the GitHub repository so you can
work on the project locally. In a terminal, run:

.. code-block:: bash

    git clone git@github.com:theirc/serviceinfo.git
    cd serviceinfo/


.. _backend-setup:

Frontend Setup
--------------

The frontend runs separately from the backend.

The Javascript dependencies are installed by Node's NPM, both for build
tools and frontend modules. Javascript libraries for the frontend app are
installed from NPM and then packaged for the browser by Browserify. You'll
need to install Node, which includes npm, in order to build the frontend
application if you'd like to run it.

On Mac, you can install Node with brew::

    brew install node

On Ubuntu and other Linux distributions, you should download and build the
latest version of Node v0.10.*.   (Newer versions might not work.)

Standard package managers rarely have the most recent
versions of Node that include NPM. You can download it from
http://nodejs.org/download/ and follow the standard build instructions::

    wget https://nodejs.org/download/release/latest-v0.10.x/node-v0.10.40.tar.gz
    tar -zxf node-v0.10.40.tar.gz
    cd node-v0.10.40/
    ./configure
    make
    sudo make install
    cd ..

WARNING: Do not build node while your ServiceInfo virtualenv is active.
Node expects Python 2.7 and our virtualenv uses 3.4.

With Node installed, you can install all frontend dependencies with `npm`::

    npm install


Backend Setup
-------------

Below you will find basic setup instructions for the
project. To begin you should have the following applications installed on your
local development system:

- Python == 3.4
- `pip >= 6.1.0 <http://www.pip-installer.org/>`_
- `virtualenv >= 1.11 <http://www.virtualenv.org/>`_
- `virtualenvwrapper >= 3.0 <http://pypi.python.org/pypi/virtualenvwrapper>`_
- Postgres >= 9.1 (9.3 recommended)
- PostGIS
- git >= 1.7
- node
- npm
- Elasticsearch 1.7.4

The deployment uses SSH with agent forwarding so you'll need to enable agent
forwarding if it is not already by adding ``ForwardAgent yes`` to your SSH config.


Getting Started
~~~~~~~~~~~~~~~

If you need Python 3.4 installed on Ubuntu, you can use this PPA::

    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install python3.4-dev

The tool that we use to deploy code is called `Fabric
<http://docs.fabfile.org/>`_, which is not yet Python 3.x compatible. So,
we need to install that globally in our Python 2.x environment::

    sudo pip install fabric==1.10.1

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    mkvirtualenv --python=<path>/python3.4 serviceinfo
    pip install -U pip
    pip install -U -r requirements/dev.txt

In order to use JavaScript tools that npm installs, you'll need to add
``node_modules/.bin`` to the *front* of your PATH. One way to do that is to
add this to your virtualenvs' postactivate script::

    if [ -d node_modules/.bin ] ; then
        if printenv PATH | grep --quiet node_modules/.bin ; then
            echo "node_modules already on PATH: $PATH"
        else
            echo "Adding node_modules to PATH"
            PATH=$(pwd)/node_modules/.bin:$PATH
        fi
    fi


Install the needed Javascript tools and libraries::

    npm install

Then create a local settings file and set your ``DJANGO_SETTINGS_MODULE`` to use it
and also to use the javascript tools just installed::

    cp service_info/settings/local.example.py service_info/settings/local.py
    echo "export DJANGO_SETTINGS_MODULE=service_info.settings.local" >> $VIRTUAL_ENV/bin/postactivate
    echo "unset DJANGO_SETTINGS_MODULE" >> $VIRTUAL_ENV/bin/postdeactivate
    echo "PATH=$PWD/node_modules/.bin:\$PATH" >> $VIRTUAL_ENV/bin/postactivate

Exit the virtualenv and reactivate it to activate the settings just changed::

    deactivate
    workon serviceinfo

Now you can run the tests::

    ./run_tests.sh

Enabling the search engine
~~~~~~~~~~~~~~~~~~~~~~~~~~

Running Elasticsearch can be as simple as unpacking it and then::

    cd elasticsearch-1.7.4 && bin/elasticsearch

(This requires Java.)

You should add this to the bottom of ``config/elasticsearch.yml``
to limit it to a simple single-node configuration which only services the local
machine::

    network.host: 127.0.0.1
    node.local: true
    discovery.zen.ping.multicast.enabled: false

If you have less than 10% disk space free, you'll need to make more space available
or add this to the bottom of ``config/elasticsearch.yml``::

    cluster.routing.allocation.disk.threshold_enabled: false

Use the Django management commands ``rebuild_index``, ``clear_index``, or
``update_index`` to maintain the search index.  (The index will be updated in real
time after some types of changes.)

Disabling search indexing
~~~~~~~~~~~~~~~~~~~~~~~~~

Add this to ``local.py``::

    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'

Running locally
~~~~~~~~~~~~~~~

Create the Postgres database and run the initial migrate::

    createdb -E UTF-8 service_info
    psql service_info -c "CREATE EXTENSION postgis;"
    python manage.py migrate

You should now be able to build the frontend and run the development API server::

    gulp

Follow the instructions for CMS configuration in the CMS setup document or
just run the ``create_minimal_cms`` management command.

Now visit http://localhost:4005/ in your browser.

If you need to debug the Javascript, you might prefer to skip running Closure.
You can skip closure by adding the ``--fast`` option to gulp::

    gulp --fast
