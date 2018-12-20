MODULE_NAME = neo4j-fdw
PYTHON ?= python
PKGDIR = $$($(PYTHON) -c "import site; print(site.getsitepackages()[0])")
NAME = $$($(PYTHON) setup.py --name)
VERSION = $$($(PYTHON) setup.py --version)
PYVERSION = $$($(PYTHON) -c "import sys; print(sys.version[:3])")

.PHONY: all install test uninstall clean

all: install

test:
	@./scripts/test.sh

install:
	@$(PYTHON) setup.py install

uninstall:
	@rm -f $(PKGDIR)/$(NAME)-$(VERSION)-py$(PYVERSION).egg

clean:
	@$(PYTHON) setup.py clean
