SPRINGER_DIR    = springer-nature
PPSN_DIR        = ppsn2026
PPSN_HOSTS_DIR  = ppsn2026-ivf-hosts
CLEI_DIR        = clei2026

.PHONY: all springer springer-nature ppsn ppsn2026 ppsn-hosts \
        ppsn2026-ivf-hosts ppsn-hosts-assets papers clean \
        view view-springer view-springer-nature \
        view-ppsn view-ppsn2026 view-ppsn-hosts view-ppsn2026-ivf-hosts \
        clei clei2026 view-cleli view-ppsn2026-ivf-hosts \
        install-deps

all: springer-nature

springer: springer-nature

springer-nature:
	$(MAKE) -C $(SPRINGER_DIR) all

ppsn: ppsn2026

ppsn2026:
	$(MAKE) -C $(PPSN_DIR) all

ppsn-hosts:
	$(MAKE) -C $(PPSN_HOSTS_DIR) all

ppsn2026-ivf-hosts: ppsn-hosts

ppsn-hosts-assets:
	$(MAKE) -C $(PPSN_HOSTS_DIR) assets

clei: clei2026

clei2026:
	$(MAKE) -C $(CLEI_DIR) all

papers: springer-nature ppsn2026 ppsn-hosts clei2026

clean:
	$(MAKE) -C $(SPRINGER_DIR) clean
	$(MAKE) -C $(PPSN_DIR) clean
	$(MAKE) -C $(PPSN_HOSTS_DIR) clean
	$(MAKE) -C $(CLEI_DIR) clean

view: view-springer-nature

view-springer: view-springer-nature

view-springer-nature: springer-nature
	$(MAKE) -C $(SPRINGER_DIR) view

view-ppsn: view-ppsn2026

view-ppsn2026: ppsn2026
	$(MAKE) -C $(PPSN_DIR) view

view-ppsn-hosts: ppsn-hosts
	$(MAKE) -C $(PPSN_HOSTS_DIR) view

view-ppsn2026-ivf-hosts: view-ppsn-hosts

view-cleli: clei2026
	$(MAKE) -C $(CLEI_DIR) view

install-deps:
	$(MAKE) -C $(SPRINGER_DIR) install-deps
