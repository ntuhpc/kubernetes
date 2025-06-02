#
# NTUHPC
# Kubernetes
# Makefile
#


KUBECTL:=kubectl

.PHONY: diff clean

apply: manifests.yaml
	$(KUBECTL) apply --force-conflicts --server-side -f $<

diff: manifests.yaml
	$(KUBECTL) diff -f $<

manifests.yaml:
	$(KUBECTL) kustomize --enable-helm base >$@

clean:
	rm -rf manifests.yaml
