Automated SLA Tool
==================

Automated SLA Tool is a reporting tool which uses reads excel spreadsheets
and combines the data to report on help desk metrics.

.. literalinclude:: main.py
   :language: python
   :emphasize-lines: 12,15-18
   :linenos:

.. code-block:: python
   :linenos:

    my_ui = Ui()
    my_obj = SlaReport(report_date=report_date)
    my_ui.object = my_obj
    my_ui.run()

.. warning::

   Currently in early development.

Features
--------

- Build reports tying together data from different sources.
- Make things faster

Installation
------------

Install $project by running:

    install project

Contribute
----------

- Issue Tracker: TBD
- Source Code: https://github.com/michaelscales88/automated_sla_toolv3

Support
-------

If you are having issues, please let us know.
We have a mailing list located at: mscales@mindwireless.com

License
-------

The project is licensed under the BSD license.