## Task 1

Persistent call count tracking was implemented via docker volumes.

**Peristent visits:**
![Persistent visits](persistent_visits.png)

## Task 2

A ConfigMap for `config.json` and a ConfigMap for injecting environment variables were created and their effect verified.

**ConfigMap verification:**
![ConfigMap](config_map_verification.png)

## Task 3

A persistent volume was used to make `/visits` endpoint behave in a persistent manner.

**Provisioning success:**
![Provisioning success](provisioning_success.png)

**Persistence proof:**
![Persistence proof](persistence_proof.png)
