base:
  "*":
    - project
    - devs
  'environment:vagrant':
    - match: grain
    - vagrant.env
    - vagrant.secrets
  'environment:staging':
    - match: grain
    - staging.env
    - staging.secrets
  'environment:production':
    - match: grain
    - production.env
    - production.secrets
