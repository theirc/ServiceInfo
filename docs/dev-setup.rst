Development Setup
=================


.. _clone-the-repository:

Clone the Repository
--------------------

To get started, you'll first need to clone the GitHub repository so you can
work on the project locally. In a terminal, run:

.. code-block:: bash

    git clone git@github.com:theirc/ServiceInfo-project.git
    cd ServiceInfo-project/


.. _backend-setup:

Frontend Setup
--------------

The frontend runs separately from the backend.

The Javascript dependencies are installed by Node's NPM, both for build
tools and frontend modules. Javascript libraries for the frontend app are
installed from NPM and then packaged for the browser by Browserify. You'll
need to install Node, which includes npm, in order to build the frontend
application if you'd like to run it.

On Mac, you can install Node with brew.

    brew install node

On Ubuntu and other Linux distributions, you should download and build the
latest version of Node. Standard package managers rarely have the most recent
versions of Node that include NPM. You can download it from http://nodejs.org/download/ and follow the standard build instructions

    tar -zxvf node-v0.10.35.tar.gz
    cd node-v0.10.35/
    ./configure
    make
    sudo make install
    cd ..

With Node installed, you can install all frontend dependencies with `npm`.

    npm install


Backend Setup
-------------

Below you will find basic setup instructions for the
project. To begin you should have the following applications installed on your
local development system:

- Python >= 3.4 (3.4 recommended)
- `pip >= 1.5 <http://www.pip-installer.org/>`_
- `virtualenv >= 1.11 <http://www.virtualenv.org/>`_
- `virtualenvwrapper >= 3.0 <http://pypi.python.org/pypi/virtualenvwrapper>`_
- Postgres >= 9.1 (9.3 recommended)
- PostGIS
- git >= 1.7
- node
- npm

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

    mkvirtualenv --python=/usr/bin/python3.4 ServiceInfo-project
    $VIRTUAL_ENV/bin/pip install -r $PWD/requirements/dev.txt

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
    workon ServiceInfo-project

Now you can run the tests::

    ./run_tests.sh

Running locally
~~~~~~~~~~~~~~~

Create the Postgres database and run the initial migrate::

    createdb -E UTF-8 service_info
    psql service_info -c "CREATE EXTENSION postgis;"
    python manage.py migrate

You should now be able to build the frontend and run the development API server::

    gulp

Now visit http://localhost:8000/ in your browser.

If you need to debug the Javascript, you might prefer to skip running Closure.
You can skip closure by adding the ``--fast`` option to gulp::

    gulp --fast
