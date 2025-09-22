Operational Notes
=================

Busy-State Policy
-----------------
- Only one pull or update operation may run at a time.
- POST /pull-data or /update-analysis returns 409 with {"busy": true} if another operation is in progress.
- Tests use dependency injection/mocks to simulate busy states.

Idempotency Strategy
-------------------
- Duplicate pulls do not insert duplicate rows.
- Database uniqueness constraints prevent accidental duplicates.

Uniqueness Keys
---------------
- Applicant entries are uniquely identified by (name, program, term, school).
- These keys are used to enforce idempotency and maintain consistent analysis.

Troubleshooting
---------------
- If pytest fails due to database connectivity, check `DATABASE_URL`.
- Ensure the Postgres instance is running and accessible.
- HTML rendering warnings (Sphinx autodoc) may appear if dependencies are missing; these do not break docs.
- For CI, confirm all Python packages in `requirements.txt` are installed.
