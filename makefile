#
# NTUHPC
# Kubernetes
# Makefile
#

KUBECTL:=kubectl

.PHONY: apply

apply:
	 $(KUBECTL) kustomize --enable-helm base | $(KUBECTL) apply --force-conflicts --server-side -f -      
