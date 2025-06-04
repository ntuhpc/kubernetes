import csv
import os
import yaml

# === Config ===
CLUSTER_NAME = "default"
CLUSTER_SERVER = "https://18.140.123.46:6443"
CA_DATA = "<YOUR_BASE64_CA_CERTIFICATE>"  # Placeholder for CA cert
RESOURCE_QUOTA = {
    "requests.cpu": "1",
    "limits.cpu": "2",
    "requests.memory": "2Gi",
    "limits.memory": "4Gi",
    "requests.nvidia.com/gpu": "0"
}

# === Paths ===
OUTPUT_DIR = "kubeconfigs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Templates ===

def generate_namespace_yaml(team):
    return {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": team}
    }

def generate_serviceaccount_yaml(user, team):
    return {
        "apiVersion": "v1",
        "kind": "ServiceAccount",
        "metadata": {"name": user, "namespace": team}
    }

def generate_rolebinding_yaml(user, team):
    return {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "RoleBinding",
        "metadata": {"name": f"{team}-{user}-binding", "namespace": team},
        "subjects": [{"kind": "ServiceAccount", "name": user, "namespace": team}],
        "roleRef": {"kind": "ClusterRole", "name": "user", "apiGroup": "rbac.authorization.k8s.io"}
    }

def generate_resourcequota_yaml(team):
    return {
        "apiVersion": "v1",
        "kind": "ResourceQuota",
        "metadata": {"name": "quota", "namespace": team},
        "spec": {"hard": RESOURCE_QUOTA}
    }

def generate_kubeconfig(user):
    return {
        "apiVersion": "v1",
        "clusters": [{
            "cluster": {
                "certificate-authority-data": CA_DATA,
                "server": CLUSTER_SERVER
            },
            "name": CLUSTER_NAME
        }],
        "contexts": [{
            "context": {
                "cluster": CLUSTER_NAME,
                "user": user
            },
            "name": CLUSTER_NAME
        }],
        "current-context": CLUSTER_NAME,
        "kind": "Config",
        "preferences": {},
        "users": [{
            "name": user,
            "user": {"token": "dummy-token-placeholder"}
        }]
    }

def write_yaml(obj, path):
    with open(path, "w") as f:
        yaml.safe_dump(obj, f, sort_keys=False)

# === Main Execution ===

def main(csv_path):
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        users = [row['username'] for row in reader]

    if len(users) > 56:
        raise ValueError("Cannot provision more than 56 users!")

    for idx, user in enumerate(users):
        team = f"team{idx+1}"
        user_dir = os.path.join(OUTPUT_DIR, user)
        os.makedirs(user_dir, exist_ok=True)
        
        print(f"Generating YAMLs for {user} in {team}")
        
        # 1. Namespace
        write_yaml(generate_namespace_yaml(team), 
                  os.path.join(user_dir, "00-namespace.yaml"))
        
        # 2. ServiceAccount
        write_yaml(generate_serviceaccount_yaml(user, team),
                  os.path.join(user_dir, "01-serviceaccount.yaml"))
        
        # 3. RoleBinding
        write_yaml(generate_rolebinding_yaml(user, team),
                  os.path.join(user_dir, "02-rolebinding.yaml"))
        
        # 4. ResourceQuota
        write_yaml(generate_resourcequota_yaml(team),
                  os.path.join(user_dir, "03-resourcequota.yaml"))
        
        # 5. Kubeconfig
        write_yaml(generate_kubeconfig(user),
                  os.path.join(user_dir, "kubeconfig.yaml"))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python provision_users.py participants.csv")
        sys.exit(1)
    main(sys.argv[1])

