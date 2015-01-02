IRC's Service Mapper
====================

Please see the `documentation`_ for more information, including
`Development Setup`_ to configure your local development environment.

.. _documentation: https://github.com/theirc/Service-Mapper/tree/master/docs
.. _Development Setup: https://github.com/theirc/Service-Mapper/blob/master/docs/dev-setup.rst


Frontend Setup
--------------

The Service Mapper frontend runs separately from the backend.

Prerequisites
'''''''''''''

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

Build Instructions
''''''''''''''''''

You'll need to setup the frontend build tools and run them to
produce the frontend assets required to run.

    cd frontend/
    npm install

The bundled Javascript can be rebuilt at any time with a simple make

    make
