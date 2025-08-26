Structure
=========

Here is the project structure

.. code-block::

	p4lantir/
	├── doc/					(source-code doc)
	│   └── source/				(source of doc)
	│
	├── imgs/					(p4lentir's logos)
	├── src/					
	│   └── p4lantir/			(p4lentir's source-code)
	│
	├── pyproject.toml			(python package description)
	├── requirements*.txt		(package requirements)
	├── README.md				(main README uploaded on pypi and github)
	├── CONTRIBUTING.md			(contributing guidelines)
	└── LICENSE.txt				(license of the project)

Here is the module structure

.. code-block::

	p4lantir/src/p4lantir/
	├── mitm/					(mitm-related code)
	│   ├── mitm_utils.py		(utils function for mitm (e.g ip forwarding, arpspoofing,..))
	│   └── proxy_server.py		(internal proxy server that intercepts messages)
	│
	├── widgets/				(terminal ui related code)
	│   ├── app_ui.py			(main UI of the app)
	│   ├── enter_screen.py		(launch screen of the app)
	│   └── logger.py			(custom logger for the app)
	│
	├── config.py				(config and banner of the module)
	├── utils.py				(utils functions (e.g logging setup or args parsing))
	└── __main__.py				(main of the module, called when executed)