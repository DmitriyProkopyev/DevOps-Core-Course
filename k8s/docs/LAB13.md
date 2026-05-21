## Task 1

**ArgoCD setup:**
![ArgoCD Setup](argocd_setup.png)

**ArgoCD CLI setup:**
![ArgoCD CLI setup](argocd_cli_setup.png)

## Task 2

**Application in ArgoCD UI:**
![Application in ArgoCD UI](application_in_argo_cd_ui.png)

**Synced application:**
![Synced application](synced_application.png)

**ArgoCD initial sync:**
![ArgoCD initial sync](argocd_initial_sync.png)

**ArgoCD out of sync after change:**
![argocd_out_of_sync](argocd_out_of_sync.png)

**ArgoCD resynced::**
![ArgoCD resynced](argocd_resynced.png)

## Task 3

> Document the deployment workflow difference

The deployment workflow for `dev` and `prod` differs primarily in that `dev` is set to sync automatically whenever the repository state and the deployment state diverge. On the other hand, `prod` divergence is tracked but only synced upon manual request to avoid risky redeployments.

**Separate ArgoCD applications:**
![Separate ArgoCD applications](separate_argocd_applications.png)
