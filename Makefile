.PHONY: build install dist rpm_sources srpm rpm pypi clean

PROJECT := yconfig
PYTHON := python
RPM_SOURCES_PATH := ~/rpmbuild/SOURCES

build:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install --skip-build

dist: clean
	$(PYTHON) setup.py sdist

rpm_sources: dist
	cp dist/* $(RPM_SOURCES_PATH)/

srpm: rpm_sources
	rpmbuild -bs python-$(PROJECT).spec

rpm: rpm_sources
	rpmbuild -ba python-$(PROJECT).spec

pypi: clean
	$(PYTHON) setup.py sdist upload

clean:
	rm -rf build dist $(PROJECT).egg-info *.pyc