## Task 1

The configuration and directory structure have been initialized according to the task statement.

**Connectivity test:**
```bash
cd ansible/
ansible -i inventory/hosts.ini all -m ping
ansible webservers -a "uname -a"
```

[Connectivity proof](connectivity_proof.png)

## Task 2

Then, dedicated roles and configurations were created:
1. **Common:** a role responsible for updating the atp cache (for package installation), installing the essential tools, and selecting the uniform timezone (Europe/Moscow as of now).
2. **Docker:** a role responsible for setting up docker daemon, adding the current user to the docker group, restarting it when needed.

**First provisining run:**
```bash
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml
```

[Ansible first run](ansible_first_run.png)

**Second provisining run to demonstrate idempotency:**
```bash
ansible-playbook -i inventory/hosts.ini playbooks/provision.yml
```

[Ansible second run](ansible_second_run.png)

> Question: Which tasks changed first time? Why?

Tasks with changed status:
- Ensure apt cache is up to date
- Install common packages
- Set system timezone
- Add docker repository
- Install docker via ubuntu repo
- Add ubuntu to docker group
- Install python3-docker for Ansible modules

The reason for change is that the conditions attached to tasks have shown that currently the system does not meet the desired state, and thus the tasks should be performed.

> Question: Why nothing changed second time?

Nothing changed on the second run because the conditions attached to the tasks have shown that the system meets the target state, and therefore there is no need for changes.
