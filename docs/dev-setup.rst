Development Setup
=================


.. _clone-the-repository:

Clone the Repository
--------------------

To get started, you'll first need to clone the GitHub repository so you can
work on the project locally. In a terminal, run:

.. code-block:: bash

    git clone git@github.com:theirc/Service-Mapper.git
    cd Service-Mapper/


.. _frontend-setup:

Frontend Setup
--------------

Once you've cloned the project, open the ``frontend`` directory::

    cd frontend/

Next run a basic HTTP server with Python:

.. code-block:: bash

    # Python <= 2.7
    python -m SimpleHTTPServer
    # Python >= 3.0
    python -m http.server

Now visit http://localhost:8000/ in your browser.


.. _backend-setup:

Backend Setup
-------------

Below you will find basic setup instructions for the Service-Mapper
project. To begin you should have the following applications installed on your
local development system:

- Python >= 3.4 (3.4 recommended)
- `pip >= 1.5 <http://www.pip-installer.org/>`_
- `virtualenv >= 1.11 <http://www.virtualenv.org/>`_
- `virtualenvwrapper >= 3.0 <http://pypi.python.org/pypi/virtualenvwrapper>`_
- Postgres >= 9.1 (9.3 recommended)
- git >= 1.7

The deployment uses SSH with agent forwarding so you'll need to enable agent
forwarding if it is not already by adding ``ForwardAgent yes`` to your SSH config.


Getting Started
~~~~~~~~~~~~~~~

If you need Python 3.4 installed, you can use this PPA::

    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install python3.4-dev

The tool that we use to deploy code is called `Fabric
<http://docs.fabfile.org/>`_, which is not yet Python 3.x compatible. So,
we need to install that globally in our Python 2.x environment::

    sudo pip install fabric==1.10.1

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    mkvirtualenv --python=/usr/bin/python3.4 service_mapper
    $VIRTUAL_ENV/bin/pip install -r $PWD/requirements/dev.txt

Then create a local settings file and set your ``DJANGO_SETTINGS_MODULE`` to use it::

    cp service_mapper/settings/local.example.py service_mapper/settings/local.py
    echo "export DJANGO_SETTINGS_MODULE=service_mapper.settings.local" >> $VIRTUAL_ENV/bin/postactivate
    echo "unset DJANGO_SETTINGS_MODULE" >> $VIRTUAL_ENV/bin/postdeactivate

Exit the virtualenv and reactivate it to activate the settings just changed::

    deactivate
    workon service_mapper

Now, create the Postgres database and run the initial syncdb/migrate::

    createdb -E UTF-8 service_mapper
    psql service_mapper -c "CREATE EXTENSION postgis;"
    python manage.py syncdb
    python manage.py migrate

You should now be able to run the development server::

    python manage.py runserver
