base:
  "*":
    - project
    - devs
  'environment:staging':
    - match: grain
    - staging.env
    - staging.secrets
  'environment:production':
    - match: grain
    - production.env
    - production.secrets
