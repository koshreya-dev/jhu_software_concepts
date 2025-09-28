GradCafe Data Analysis
======================

Overview & Setup
----------------
- Run the Flask app: ``python -m module_4.src.front_end.app_factory``
- Required environment variables:
  - ``DATABASE_URL`` (e.g., ``postgresql://postgres:jhu123@localhost:5432/postgres``)
- Run tests: ``pytest -m "web or buttons or analysis or db or integration"``

Architecture
------------
- **Web layer:** Flask routes serve ``/analysis``, ``/pull-data``, ``/update-analysis``.
- **ETL layer:** ``scrape.py``, ``clean.py``, ``load_data.py`` handle scraping, cleaning, and inserting data.
- **Database layer:** PostgreSQL stores applicant data and supports queries for analysis.

API Reference
-------------
.. automodule:: scrape
    :members:
    :undoc-members:

.. automodule:: clean
    :members:
    :undoc-members:

.. automodule:: load_data
    :members:
    :undoc-members:

.. automodule:: query_data
    :members:
    :undoc-members:

.. automodule:: flask_app
    :members:
    :undoc-members:

Testing Guide
-------------
- Run marked tests:

  .. code-block:: bash

      pytest -m "web or buttons or analysis or db or integration"

- **Selectors:** ``data-testid="pull-data-btn"`` and ``data-testid="update-analysis-btn"``
- **Fixtures / test doubles:** ``FakePool`` used to simulate DB, fake scraper injected for tests.

.. toctree::
   :maxdepth: 2
   :caption: Additional:

   operational_notes