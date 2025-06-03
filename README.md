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

Follow these steps to access the Kubernetes cluster:

1. Install [kubectl](https://kubernetes.io/docs/tasks/tools/) and Install [kubelogin](https://github.com/int128/kubelogin?tab=readme-ov-file#setup).
2. Create the kubeconfig file ie. `ntuhpc.yaml`:

```yaml
apiVersion: v1
clusters:
  - cluster:
      certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJkekNDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkKZG1WeUxXTmhRREUzTkRnM05EVTRORGt3SGhjTk1qVXdOakF4TURJME5EQTVXaGNOTXpVd05UTXdNREkwTkRBNQpXakFqTVNFd0h3WURWUVFEREJock0zTXRjMlZ5ZG1WeUxXTmhRREUzTkRnM05EVTRORGt3V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFTUHc0SHhBSnhXdDAwdkxoZ0hQQ0UyUk1yc3E1cjZDN1hlYVEvRFBkV0IKU2o3RnlsTE5zQStPOTVmMWM2UFJXaGZpd1BkTFR0U2RkcVZBQjlUYUIvczVvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVTNuSGs4OTR2S0pRS0pBVDFyQzVjCnQrVjRkaG93Q2dZSUtvWkl6ajBFQXdJRFNBQXdSUUlnRjE4aGU4N2JDVDZhYTZyQmNqY1gzVU1leVZwQUlLT2YKeG95OTI2eExwR1VDSVFDMzRHd0JxNzVaRzk0WU91bGJrUWcwK2c0dEx6UVhFSG1iODdpNzlXcndPUT09Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
      server: https://p.ntuhpc.org:6443
    name: ntuhpc
contexts:
  - context:
      cluster: ntuhpc
      user: ntuhpc
    name: ntuhpc
current-context: ntuhpc
kind: Config
preferences: {}
users:
  - name: ntuhpc
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1
        args:
          - oidc-login
          - get-token
          - --oidc-issuer-url=https://p.ntuhpc.com/dex
          - --oidc-client-id=k8s-control.ntuhpc.org
          - --oidc-extra-scope=email
          - --oidc-extra-scope=profile
          - --skip-open-browser
        command: kubectl
        env: null
        interactiveMode: Never
        provideClusterInfo: false
```

3. Configure `kubectl` to use the kubeconfig file:

```sh
export KUBECONFIG=ntuhpc.yaml
```

or pass `--kubeconfig ntuhpc.yaml` option when using `kubectl` commands.

4. Verify the cluster access:

```sh
kubectl version
```

## Contributing

Please submit a pull request to make changes.

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
    requests.cpu: "10" # total CPU requested (cores)
    limits.cpu: "20" # total CPU limit
    requests.memory: "32Gi" # total memory requested
    limits.memory: "64Gi" # total memory limit
    requests.nvidia.com/gpu: "4" # total GPUs requested (NVIDIA GPU)
```

4. Once the end users are done with the cluster, cleanup by deleting the namespace:

```sh
kubectl delete namespace team
```

This will automatically delete all resources within the namespace, including the user ServiceAccount and RoleBinding.

### References

- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Create Kubernetes user restricted to one namespace with resource limits](https://raymii.org/s/tutorials/Create_Kubernetes_user_restricted_to_one_namespace_with_resource_limits.html)
