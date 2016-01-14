# development helpers for lndirs

help:
	@echo Targets:
	@echo "  dev         - install as development mode (symlinks)"
	@echo "  check       - check project"
	@echo "  clean       - clean generated build files"

dev: clean
	sudo apt-get -y install python3-pip
	pip3 install --user --upgrade pip
	pip3 install --user --upgrade flake8 pytest tox
	pip3 install --user --process-dependency-links -e .

check:
	flake8 .
	tox	

clean:
	rm -rfv $(shell find . \
	-name "build" -o \
	-name "dist" -o \
	-name "__pycache__" -o \
	-name "*~" -o \
	-name "*.bak" -o \
	-name "*.vpp~*" -o \
	-name "*.egg-info" -o \
	-name "*.eggs" -o \
	-name "*.cache" -o \
	-name ".tox")

 
# Copyright (C) 2015 Petri Heinilä, License LGPL 2.1