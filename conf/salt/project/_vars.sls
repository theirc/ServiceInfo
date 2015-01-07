{% set root_dir = "/var/www/" + pillar['project_name'] + "/" %}

{% macro get_primary_ip(ifaces) -%}
  {{ ifaces.get(salt['pillar.get']('primary_iface', 'eth0'), {}).get('inet', [{}])[0].get('address') }}
{%- endmacro %}

{% macro build_path(root, name) -%}
  {{ root }}{%- if not root.endswith('/') -%}/{%- endif -%}{{ name }}
{%- endmacro %}

{% macro path_from_root(name) -%}
  {{ build_path(root_dir, name) }}
{%- endmacro %}

{% set auth_file = path_from_root(".htpasswd") %}
{% set current_ip = grains['ip_interfaces'].get(salt['pillar.get']('primary_iface', 'eth0'), [])[0] %}
{% set log_dir = path_from_root('log') %}
{% set public_dir = path_from_root('public') %}
{% set services_dir = path_from_root('services') %}
{% set ssh_dir = "/home/" + pillar['project_name'] + "/.ssh/" %}
{% set ssl_dir = path_from_root('ssl') %}
{% set source_dir = path_from_root('source') %}
{% set static_dir = path_from_root('public/static') %}
{% set venv_dir = path_from_root('env') %}

# This fixes a regresion in Salt https://github.com/caktus/django-project-template/issues/137
{% set web_minions = salt['mine.get']('roles:web', 'network.interfaces', expr_form='grain') %}
{% set worker_minions = salt['mine.get']('roles:worker', 'network.interfaces', expr_form='grain') %}
{% set app_minions = salt['mine.get']('roles:(worker|web)', 'network.interfaces', expr_form='grain_pcre') %}
{% set balancer_minions = salt['mine.get']('roles:balancer', 'network.interfaces', expr_form='grain') %}
