Installation
============

This page explains how to setup your environment to develop the **p4lantir**'s source code and documentation.


Development
-------------
* Install the dev dependencies at the system-levevl
* Fork the github repository to your account and clone it
* Setup the virtual-environment for python
* Install the python dev dependencies

.. code-block:: sh
	:linenos:

	# Uncomment one of the following lines
	# apt update && apt install dsniff iptables
	# pacman -S dsniff iptables

	git clone [url of your fork]
	cd p4lantir
	
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements-dev.txt


Documentation
-------------

All the files related to this documentation are under the directory `doc/source`. To compile the documentation, you need to first follow the instructions in the previous development section (except that you do not have to install the system-level dependencies). Then you can run : 

.. code-block:: sh
	:linenos:

	cd doc
	make html


This will generate the code-documentation in HTML format.
