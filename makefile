#
# NTUHPC
# Kubernetes
# Makefile
#

KUBECTL:=kubectl

.PHONY: diff

apply:
	 $(KUBECTL) kustomize --enable-helm base | $(KUBECTL) apply --force-conflicts --server-side -f -

diff:
	 $(KUBECTL) kustomize --enable-helm base | $(KUBECTL) diff -f -
