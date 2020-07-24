MODULE_NAME    = neo4j-fdw
NAME           = $$($(PYTHON) setup.py --name)
EXTVERSION        = $(shell grep default_version ./$(MODULE_NAME).control | sed -e "s/default_version[[:space:]]*=[[:space:]]*'\([^']*\)'/\1/")
DATA           =  $(filter-out $(wildcard sql/*--*.sql),$(wildcard sql/*.sql))
DOCS           = README.adoc
MODULEDIR      = neo4j-fdw

PYTHON        ?= python
PKGDIR        = $$($(PYTHON) -c "import site; print(site.getsitepackages()[0])")
PYVERSION     = $$($(PYTHON) -c "import sys; print(sys.version[:3])")

.PHONY: all install test uninstall clean

all: install

test:
	@./scripts/test.sh

install: python_code

python_code:
	echo $(PYTHON)
	cp ./setup.py ./setup--$(EXTVERSION).py
	sed -i -e "s/__VERSION__/$(EXTVERSION)/g" ./setup--$(EXTVERSION).py
	$(PYTHON) ./setup--$(EXTVERSION).py install
	rm ./setup--$(EXTVERSION).py

clean:
	$(PYTHON) setup.py clean
	rm -f $(PKGDIR)/$(NAME)-$(EXTVERSION)-py$(PYVERSION).egg


PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
