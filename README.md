# dynatrace-ansible

Provide tenant URLs and API tokens in config.py.
Then execute "python main.py" which will make an API call to source tenant to obtain inventory and then call migrate_tenant.yml ansible playbook. Main.py also makes aditional API calls to migrate web applications and services, though those might require some fine-tunning depending on whether they are auto-injected or not.
