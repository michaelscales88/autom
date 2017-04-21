Automated SLA Tool
==================

Automated SLA Tool is a reporting tool which uses reads excel spreadsheets
and combines the data to report on help desk metrics.

..  code-block:: python

    my_ui = Ui()
    my_obj = SlaReport(report_date=report_date)
    my_ui.object = my_obj
    my_ui.run()

The simplest usage is demonstrated above. report_date takes a datetime.
generic_ui is provided as an interface to the report algorithm.

.. warning::

   This version is hardcoded to build reports for a specific help desk.
   As a result the code will not fully run on other machines. A more general version is in development.
   https://github.com/michaelscales88/falcon_reporting

Features
--------

- Automates the processing of data from multiple sources to produce a summary report.

In Development
--------------

| - Work on Logger: Currently logs are being printed to the console, but SysLog
| is available to have prints piped to a reporting Log.''
|
| - Work on DataCenter: DataCenter will process all data connections in falcon.
| Working on an event driven algorithm that makes use of the configobj AppSettings
|
| - Work on installation. Intending to implement with docker

Installation
------------

TBD - Docker

Contribute
----------

- Issue Tracker: TBD
- Source Code: https://github.com/michaelscales88/automated_sla_tool

Support
-------

If you are having issues, please let me know.
We have a mailing list located at: mscales@mindwireless.com

License
-------

The project is licensed under the BSD license.