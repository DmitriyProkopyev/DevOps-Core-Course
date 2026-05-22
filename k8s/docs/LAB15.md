## Task 1

> When to use Deployment vs StatefulSet?

Deployment optimizes for interchangeable replicas. When to use Deployment:
- When the target app is stateless
- When any replica can serve any requests
- When individual replicas are disposable

StatefulSets optimize for persistency and data stability. When to use StatefulState:
- When each replica needs a stable network identity
- When stable storage is required
- When ordered rollout and termination is necessary

> Examples of stateful workloads

- Databases: PostgreSQL, MySQL, MongoDB, and etcd.
- Distributed storage systems: Elasticsearch, Cassandra
- Stateful brokers: Kafka, RabbitMQ

> What is a headless service?

A headless Service is a Service with `clusterIP: None`. It does not have a virtual IP for load balancing, as DNS instead returns the individual Pod IPs directly, so clients can connect to specific pods. This behaviour is typically useful for StatefulSets for accessing pods via their stable network identities.

> How does DNS works with StatefulSets?

A StatefulSet typically references a headless service using the `serviceName` field. Kubernetes then gives each pod a predictable DNS name. That stable naming enables peers to find each other reliably after restarts or rescheduling.
