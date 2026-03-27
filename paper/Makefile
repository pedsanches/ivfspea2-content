SPRINGER_DIR = springer-nature
PPSN_DIR = ppsn2026

.PHONY: all springer springer-nature ppsn ppsn2026 papers clean view view-springer view-springer-nature view-ppsn view-ppsn2026 install-deps

all: springer-nature

springer: springer-nature

springer-nature:
	$(MAKE) -C $(SPRINGER_DIR) all

ppsn: ppsn2026

ppsn2026:
	$(MAKE) -C $(PPSN_DIR) all

papers: springer-nature ppsn2026

clean:
	$(MAKE) -C $(SPRINGER_DIR) clean
	$(MAKE) -C $(PPSN_DIR) clean

view: view-springer-nature

view-springer: view-springer-nature

view-springer-nature: springer-nature
	$(MAKE) -C $(SPRINGER_DIR) view

view-ppsn: view-ppsn2026

view-ppsn2026: ppsn2026
	$(MAKE) -C $(PPSN_DIR) view

install-deps:
	$(MAKE) -C $(SPRINGER_DIR) install-deps
