## Task 1

> Document roles of: Prometheus Operator, Prometheus, Alertmanager, Grafana, kube-state-metrics, node-exporter

- Prometheus Operator: automates deployment and configuration of Prometheus and related components on Kubernetes using custom resources.
- Prometheus: pulls metrics from targets over HTTP, stores them as time-series data, and evaluates alert rules and queries with PromQL.
- Alertmanager: receives alerts from Prometheus, deduplicates them, groups them, routes them, and sends notifications to specified channels.
- Grafana: reads metrics from Prometheus and turns them into dashboards, graphs, and operational views for humans.
- `kube-state-metrics`: watches the Kubernetes API and exports metrics about the state of cluster objects.
- `node-exporter`: Runs on each node and exports OS and hardware metrics like CPU, memory, disk, and network usage. 

**Prometheus components ready:**
![Prometheus components ready](prometheus_components_ready.png)
