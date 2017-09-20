ServiceInfo backups
===================


Getting a backup dump and restoring it locally
----------------------------------------------

Steps you can do ahead of time:

* Get access to the Caktus backup server (open a tech support request).

When you need to restore a backup:

* Make sure you are in your ServiceInfo project directory, and not in the ServiceInfo-IRCDeploy
  project directory::

    $ git config --get remote.origin.url
    git@github.com:theirc/serviceinfo.git

* List the files in the latest backup directory and find the most recent::

    $ backup_path=/mnt/rsnapshot/serviceinfo-prod/hourly.0/home/caktus-backup
    $ backup_filename=`ssh caktus-backup@backup.caktus.lan ls $backup_path | tail -1`

* Copy that file to your local directory and MAKE SURE it's named ``service_info.sql.bz2``. That's
  not important if you're only doing a local restore, but if you're restoring to staging, our Fabric
  scripts look for that particular filename.::

    $ scp caktus-backup@backup.caktus.lan:${backup_path}/${backup_filename} service_info.sql.bz2

It's about 3.7 MB as of Sept 2017.

* Decompress the file::

    $ bunzip2 service_info.sql.bz2

Now the file is in ``service_info.sql`` (in SQL text format).

Drop your existing local database and restore from the backup::

    $ dropdb service_info
    $ createdb --template=template0 service_info
    $ psql service_info < service_info.sql

There will be a bunch of errors related to the fact that the production dump has roles which your
local DB doesn't have. It's OK to ignore them.

Migrate the database::

    $ workon serviceinfo
    $ ./manage.py migrate --noinput

Next, we need to copy the production CMS content to your local site. The value 'localhost:8000' is
special because the 'Domain Name' is hard-coded to that value in the Django admin ("Sites" app)::

    $ ./manage.py change_cms_site --from=serviceinfo.rescue.org --to=localhost:8000

Update your media directory with the media from production::

    $ rsync -zPa -e ssh --delete caktus-backup@backup.caktus.lan:/mnt/rsnapshot/serviceinfo-prod/hourly.0/var/www/service_info/public/media public

Now run the server normally and visit 'http://localhost:4005/' to make sure things look OK::

    $ gulp

Continue to the next section to restore the staging server. When you're done, be sure to delete the
dump from your laptop::

    $ rm -f service_info.sql

Bringing up a new site using the backup dump
--------------------------------------------

The script to update the staging server expects that you have completed the steps above to copy the
database and media backups to the ServiceInfo project directory.

Now switch over to the ServiceInfo-IRCDeploy project::

    $ cd ../ServiceInfo-ircdeploy/
    $ git config --get remote.origin.url
    git@github.com:theirc/ServiceInfo-ircdeploy.git

Run the ``refresh_from_backup`` command. It takes one parameter, which is an absolute or relative
path to the main ServiceInfo project directory on your laptop (Mine is in a sibling directory named
``serviceinfo``)::

    $ workon virtualenv-with-fab
    $ fab staging refresh_from_backup:../serviceinfo

This command uploads the database dump and media to staging, stops the web server, imports the dump,
runs migrations, resets the CMS, rebuilds the ElasticSearch index, and then restarts the web server.

There is a LOT of output from this command, including the rsync progress, and multiple warnings and
errors from the DB import. There is also a warning about missing migrations which are due to a
Python 2/3 incompatibility in some third-party packages. That can be ignored for now.
