import os
import subprocess
import tempfile

import yaml

from fabric.api import env, execute, get, hide, lcd, local, put, require, run, settings, sudo, task
from fabric.colors import red
from fabric.contrib import files, project
from fabric.contrib.console import confirm
from fabric.utils import abort

DEFAULT_SALT_LOGLEVEL = 'info'
PROJECT_NAME = "service_info"
PROJECT_ROOT = os.path.dirname(__file__)
CONF_ROOT = os.path.join(PROJECT_ROOT, 'conf')

VALID_ROLES = (
    'salt-master',
    'web',
    'worker',
    'balancer',
    'db-master',
    'queue',
    'cache',
    'beat',
)


@task
def staging():
    env.environment = 'staging'
    # 54.93.66.254 Staging server on AWS Frankfurt
    env.master = 'serviceinfo-staging.rescue.org'
    env.hosts = [env.master]


@task
def production():
    env.environment = 'production'
    # 54.93.51.232
    env.master = 'serviceinfo.rescue.org'
    env.hosts = [env.master]


def get_vagrant_ssh_config_value(name):
    """
    Return the value of the named ssh config parm from vagrant.
    (Run 'vagrant ssh-config' to see what the available parms are.)
    """
    cmd = "vagrant ssh-config | awk '/ %s / {print $2;}'" % name
    return subprocess.check_output(cmd, shell=True).strip()


@task
def vagrant_first_time():
    # Use this the first time deploying to the vagrant VM, it'll
    # use Vagrant's default ssh user.  After that, you can use the
    # 'vagrant' target and connect in as your own user.
    env.environment = 'vagrant'

    # Use built-in vagrant ssh.  This'll probably use the local
    # port 2222 that redirects to wherever vagrant is listening
    # for ssh connections, but we don't really care.
    env.user = get_vagrant_ssh_config_value('User')
    host = get_vagrant_ssh_config_value('HostName')
    port = get_vagrant_ssh_config_value('Port')
    env.hosts = ['{user}@{host}:{port}'.format(user=env.user, host=host, port=port)]
    env.key_filename = get_vagrant_ssh_config_value('IdentityFile')
    env.master = host


@task
def vagrant():
    # Use dev's own user, directly to port 22 on the VM
    env.environment = 'vagrant'
    env.master = '33.33.33.10'
    env.hosts = [env.master]


@task
def setup_master():
    """Provision master with salt-master."""
    with settings(warn_only=True):
        with hide('running', 'stdout', 'stderr'):
            installed = run('which salt')
    if not installed:
        sudo('apt-get update -qq -y')
        sudo('apt-get install python-software-properties -qq -y')
        sudo('add-apt-repository ppa:saltstack/salt -y')
        sudo('apt-get update -qq')
        sudo('apt-get install salt-master -qq -y')
    # make sure git is installed for gitfs
    with settings(warn_only=True):
        with hide('running', 'stdout', 'stderr'):
            installed = run('which git')
    if not installed:
        sudo('apt-get install python-pip git-core -qq -y')
        sudo('pip install -q -U GitPython')
    put(local_path='conf/master.conf', remote_path="/etc/salt/master", use_sudo=True)
    sudo('service salt-master restart')


@task
def sync():
    """Rysnc local states and pillar data to the master."""
    # Check for missing local secrets so that they don't get deleted
    # project.rsync_project fails if host is not set
    if not have_secrets():
        get_secrets()
    else:
        # Check for differences in the secrets files
        for environment in [env.environment]:
            remote_file = os.path.join('/srv/pillar/', environment, 'secrets.sls')
            with lcd(os.path.join(CONF_ROOT, 'pillar', environment)):
                if files.exists(remote_file):
                    get(remote_file, 'secrets.sls.remote')
                else:
                    local('touch secrets.sls.remote')
                with settings(warn_only=True):
                    result = local('diff -u secrets.sls.remote secrets.sls')
                    if result.failed and not confirm(
                            red("Above changes will be made to secrets.sls. Continue?")):
                        abort("Aborted. File have been copied to secrets.sls.remote. " +
                              "Resolve conflicts, then retry.")
                    else:
                        local("rm secrets.sls.remote")
    salt_root = CONF_ROOT if CONF_ROOT.endswith('/') else CONF_ROOT + '/'
    project.rsync_project(local_dir=salt_root, remote_dir='/tmp/salt', delete=True)
    sudo('rm -rf /srv/salt /srv/pillar')
    sudo('mv /tmp/salt/* /srv/')
    sudo('rm -rf /tmp/salt/')


def have_secrets():
    """Check if the local secret files exist for all environments."""
    found = True
    for environment in [env.environment]:
        local_file = os.path.join(CONF_ROOT, 'pillar', environment, 'secrets.sls')
        found = found and os.path.exists(local_file)
    return found


@task
def get_secrets():
    """Grab the latest secrets file from the master."""
    require('environment')
    for environment in [env.environment]:
        local_file = os.path.join(CONF_ROOT, 'pillar', environment, 'secrets.sls')
        if os.path.exists(local_file):
            local('cp {0} {0}.bak'.format(local_file))
        remote_file = os.path.join('/srv/pillar/', environment, 'secrets.sls')
        get(remote_file, local_file)


@task
def setup_minion(*roles):
    """Setup a minion server with a set of roles."""
    require('environment')
    for r in roles:
        if r not in VALID_ROLES:
            abort('%s is not a valid server role for this project.' % r)
    # install salt minion if it's not there already
    with settings(warn_only=True):
        with hide('running', 'stdout', 'stderr'):
            installed = run('which salt-minion')
    if not installed:
        # install salt-minion from PPA
        sudo('apt-get update -qq -y')
        sudo('apt-get install python-software-properties -qq -y')
        sudo('add-apt-repository ppa:saltstack/salt -y')
        sudo('apt-get update -qq')
        sudo('apt-get install salt-minion -qq -y')
    config = {
        'master': 'localhost' if env.master == env.host else env.master,
        'output': 'mixed',
        'grains': {
            'environment': env.environment,
            'roles': list(roles),
        },
        'mine_functions': {
            'network.interfaces': []
        },
    }
    _, path = tempfile.mkstemp()
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    put(local_path=path, remote_path="/etc/salt/minion", use_sudo=True)
    sudo('service salt-minion restart')
    # queries server for its fully qualified domain name to get minion id
    key_name = run('python -c "import socket; print socket.getfqdn()"')
    execute(accept_key, key_name)


@task
def add_role(name):
    """Add a role to an exising minion configuration."""
    if name not in VALID_ROLES:
        abort('%s is not a valid server role for this project.' % name)
    _, path = tempfile.mkstemp()
    get("/etc/salt/minion", path)
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    grains = config.get('grains', {})
    roles = grains.get('roles', [])
    if name not in roles:
        roles.append(name)
    else:
        abort('Server is already configured with the %s role.' % name)
    grains['roles'] = roles
    config['grains'] = grains
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    put(local_path=path, remote_path="/etc/salt/minion", use_sudo=True)
    sudo('service salt-minion restart')


@task
def salt(cmd, target="'*'", loglevel=DEFAULT_SALT_LOGLEVEL):
    """Run arbitrary salt commands."""
    with settings(warn_only=True):
        sudo("salt {0} -l{1} {2} ".format(target, loglevel, cmd))


@task
def highstate(target="'*'", loglevel=DEFAULT_SALT_LOGLEVEL):
    """Run highstate on master."""
    print("This can take a long time without output, be patient")
    execute(salt, 'state.highstate', target, loglevel, hosts=[env.master])


@task
def accept_key(name):
    """Accept minion key on master."""
    sudo('salt-key --accept={0} -y'.format(name))
    sudo('salt-key -L')


@task
def delete_key(name):
    """Delete specific key on master."""
    sudo('salt-key -L')
    sudo('salt-key --delete={0} -y'.format(name))
    sudo('salt-key -L')


@task
def deploy(loglevel=DEFAULT_SALT_LOGLEVEL):
    """Deploy to a given environment by pushing the latest states and executing the highstate."""
    require('environment')
    if env.environment != "local":
        sync()
    target = "-G 'environment:{0}'".format(env.environment)
    salt('saltutil.sync_all', target, loglevel)
    highstate(target)


@task
def build():
    local("gulp build")


@task
def makemessages():
    """
    Find all the translatable English messages in our source and
    pull them out into locale/en/LC_MESSAGES/django.po
    """
    local("python manage.py makemessages --ignore 'conf/*' --ignore 'docs/*' "
          "--ignore 'requirements/*' --ignore 'frontend/*' --ignore 'vagrant/*' "
          "--no-location --no-obsolete "
          "-l en")
    local("i18next-conv -s frontend/locales/en/translation.json -t "
          "locale/en/LC_MESSAGES/frontend.po -l en")


@task
def pushmessages():
    """
    Upload the latest locale/en/LC_MESSAGES/django.po to Transifex
    """
    local("tx push -s")


@task
def pullmessages():
    """
    Pull the latest locale/ar/LC_MESSAGES/django.po and
    locale/fr/LC_MESSAGES/django.po from Transifex.

    Then take the updated frontend.po files and update the
    french and arabic translation.json files.
    """
    local("tx pull -af")
    for lang in ('fr', 'ar'):
        local("i18next-conv "
              " -t frontend/locales/%(lang)s/translation.json"
              " -s locale/%(lang)s/LC_MESSAGES/frontend.po"
              " -l %(lang)s" % locals())
    execute(compilemessages)


@task
def compilemessages():
    """
    Compile all the .po files into the .mo files that Django
    will get translated messages from at runtime.
    """
    local("python manage.py compilemessages -l en -l ar -l fr")


@task
def manage_run(command):
    """
    Run a Django management command on the remote server.
    """
    require('environment')
    # Setup the call
    settings = '{0}.settings.{1}'.format(PROJECT_NAME, env.environment)
    manage_sh = u"DJANGO_SETTINGS_MODULE={0} /var/www/{1}/manage.sh ".format(settings, PROJECT_NAME)
    sudo(manage_sh + command, user=PROJECT_NAME)


@task
def ssh():
    """
    Convenience task to ssh to whatever host has been selected.

    E.g. ``fab production ssh``
    """
    require('environment')
    local("ssh %s" % env.hosts[0])
