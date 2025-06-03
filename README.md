# Kubernetes

Kubernetes manifests for NTUHPC.

## Setup

Before deploying manifests install:

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [helm](https://helm.sh/docs/intro/install/)

### Rook Ceph

Rook Cepth deployment has been tailored to use externally managed Ceph deployed via Proxmox PVE:

1. Deploy Ceph cluster on Proxmox PVE Web GUI
2. [Export Ceph configuration](https://rook.io/docs/rook/v1.17/CRDs/Cluster/external-cluster/provider-export/) on PVE Shell.
   - Take note of `export ...` exported environment variables.
3. Paste the `export ...` into your shell to apply the Ceph configuration.
4. Run the [Import Script](./scripts/import_rook_secrets.sh) to import secrets.

## Usage

Configure access to the Kubernetes cluster, edit manifests, then diff changes:

```
make diff
```

Apply changes if all is well:

```
make apply
```

### Namespace Provisioning

Provisioning a fresh namespace for end user teams can be done as follows. Replace `user` and `team` as appropriate:

1. Creating the namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team
```

2. Creating a `RoleBinding` to allow users to access the namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-bind
  namespace: team
roleRef:
  kind: ClusterRole
  name: namespace-user
  apiGroup: rbac.authorization.k8s.io
subjects:
  - kind: User
    name: "member0@e.ntu.edu.sg"
    apiGroup: rbac.authorization.k8s.io
  - kind: User
    name: "member1@e.ntu.edu.sg"
    apiGroup: rbac.authorization.k8s.io
 # ... include other team members ..
```

3. Create system resource quota for the namespace to limit resource usage:
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota
  namespace: team
spec:
  hard:
    requests.cpu: "10"                # total CPU requested (cores)
    limits.cpu: "20"                  # total CPU limit
    requests.memory: "32Gi"           # total memory requested
    limits.memory: "64Gi"             # total memory limit
    requests.nvidia.com/gpu: "4"      # total GPUs requested (NVIDIA GPU)
```

4. Once the end users are done with the cluster, cleanup by deleting the namespace:

```sh
kubectl delete namespace team
```

This will automatically delete all resources within the namespace, including the user ServiceAccount and RoleBinding.

## Contributing

Please submit a pull request to make changes.
### References

- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Create Kubernetes user restricted to one namespace with resource limits](https://raymii.org/s/tutorials/Create_Kubernetes_user_restricted_to_one_namespace_with_resource_limits.html)
