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

Configure access to the Kubernetes cluster, then apply manifests:

```
make apply
```
