---
title: "Rows nobody touches wait twelve hours by default for your rollup change"
summary: "Calculate Rollup Field only visits rows written or deleted since the last mass calculation, so an untouched row keeps its previous aggregate until the Mass Calculate job runs."
surface: dataverse
tip_number: 25
date: 2026-10-25
wave: "n/a - documentation-based tip; no column was created, so nothing was run against an environment"
build: "The rollup column page, learn.microsoft.com/en-us/power-apps/maker/data-platform/define-rollup-fields, fetched 2026-10-25, 69295 bytes, sha256 5971f647f10745cd0baab4acdd7ad332c68ccf7b4463dfafaf247fabda6473ba"
verified_on: 2026-10-25
verified_env: "No environment and no login - the cited Learn page fetched on 2026-10-25; no rollup column was created, no record was opened and no system job was watched run"
expires_on: 2027-04-25
cost: "Free to read; creating the column and recalculating it needs a Power Platform environment, and the page names no premium add-on. The 50,000-row and depth-10 ceilings on the online recalculation apply whatever the licence"
source: "https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-rollup-fields"
artifact: "assets/tips/25-rollup-values-wait-for-the-system-job/check-page.py"
evidence: |
  NOT EXECUTED. No tenant on this machine: no rollup column was created, no aggregate was changed, no
  record was opened and no system job was observed. One page carries every claim, fetched whole the day
  of publication, and every quoted sentence below is matched by the run.

  command: PYTHONDONTWRITEBYTECODE=1 python3 assets/tips/25-rollup-values-wait-for-the-system-job/check-page.py

  observed:
    page: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-rollup-fields
      fetched 69295 bytes
      canonical matches source: True
      [ok] A rollup column contains an aggregate value computed over the rows related to a specified row.
      [ok] The column value has been calculated per the last update time in _date column.
      [ok] The rollups are calculated by scheduled system jobs that run asynchronously in the background.
      [ok] Mass Calculate Rollup Field is a recurring job, created for each rollup column.
      [ok] It runs once, after you create or update a rollup column.
      [ok] The job recalculates the specified rollup column value in all existing records that contain this column.
      [ok] By default, the job will run 12 hours after you have created or updated a column.
      [ok] When the column is modified, the job resets to run again in 12 hours after the update.
      [ok] We recommend that an administrator adjusts the start time of a Mass Calculate Rollup Field job after the rollup column is created or modified, in such a way that it runs during nonoperational hours.
      [ok] Calculate Rollup Field is a recurring job that does incremental calculations of all rollup columns in the existing rows for a specified table.
      [ok] The incremental calculations mean that the Calculate Rollup Field job processes the rows that were created, updated, or deleted after the last Mass Calculate Rollup Field job finished execution.
      [ok] The rollup column on the form displays a calculator image, rollup value, and the time of the last calculation.
      [ok] To recalculate, select the calculator image, and then select the Recalculate button that appears.
      [ok] The maximum number of rows during the rollup refresh is limited to 50,000 rows.
      [ok] As a system administrator, you can modify the rollup job recurrence pattern, postpone, pause, or resume the rollup job.
      [ok] For the Mass Calculate Rollup Field job, the available selections are: Resume , Postpone , and Pause .
      [ok] For the Calculate Rollup Field job, the available selections are: Modify Recurrence , Resume , Postpone , and Pause .
      quotes present: 17/17
    result: every quoted sentence is still on the page, whole
    note: this checks the page only - the observation that no tenant was available is a record, not a claim this script re-tests
  exit 0

  curl of the same URL the same day: http 200, 69295 bytes,
  sha256 5971f647f10745cd0baab4acdd7ad332c68ccf7b4463dfafaf247fabda6473ba.

  Quoted sentences, in page order, each matched whole by the run:

    "A rollup column contains an aggregate value computed over the rows related to a specified row."
    "The column value has been calculated per the last update time in _date column."
    "The rollups are calculated by scheduled system jobs that run asynchronously in the background."
    "Mass Calculate Rollup Field is a recurring job, created for each rollup column."
    "It runs once, after you create or update a rollup column."
    "The job recalculates the specified rollup column value in all existing records that contain this column."
    "By default, the job will run 12 hours after you have created or updated a column."
    "When the column is modified, the job resets to run again in 12 hours after the update."
    "We recommend that an administrator adjusts the start time of a Mass Calculate Rollup Field job after the rollup column is created or modified, in such a way that it runs during nonoperational hours."
    "Calculate Rollup Field is a recurring job that does incremental calculations of all rollup columns in the existing rows for a specified table."
    "The incremental calculations mean that the Calculate Rollup Field job processes the rows that were created, updated, or deleted after the last Mass Calculate Rollup Field job finished execution."
    "The rollup column on the form displays a calculator image, rollup value, and the time of the last calculation."
    "To recalculate, select the calculator image, and then select the Recalculate button that appears."
    "The maximum number of rows during the rollup refresh is limited to 50,000 rows."
    "As a system administrator, you can modify the rollup job recurrence pattern, postpone, pause, or resume the rollup job."
    "For the Mass Calculate Rollup Field job, the available selections are: Resume , Postpone , and Pause ."
    "For the Calculate Rollup Field job, the available selections are: Modify Recurrence , Resume , Postpone , and Pause ."

  The fix rests on three of those: the form shows a calculator image with a Recalculate button under it,
  the online recalculation is capped at 50,000 related rows and a hierarchy depth of 10, and the Mass
  Calculate job's own Actions carry Resume, Postpone and Pause with no Modify Recurrence. The 12-hour
  default, the reset on modification and the incremental job's narrower row set come straight from the
  sentences that carry them.

  NOT claimed: that an untouched row reads zero or blank before the mass job runs - the page says the
  existing records are recalculated by that job and that the value corresponds to the last calculation
  time in the _date column, and never describes a fresh column's pre-run value. Also not claimed: that
  the incremental job applies the edited definition to a row before the mass job has run, or that a whole
  table can be brought forward - Recalculate is one row at a time and the Mass Calculate job's actions
  offer no way to run it sooner.
---

You change a rollup column - a different filter, a different aggregate - and save it. The rows you already had keep the number from their last calculation, because nothing has recomputed them yet.

Two jobs do this work. Calculate Rollup Field is the incremental one: it only visits rows that were written or deleted since the last mass calculation finished. Mass Calculate Rollup Field is the job that goes over every existing row, and it is the one your edit scheduled, twelve hours out by default, with each further change resetting it to another twelve. So an untouched row waits for that job, and its `_date` column records when the number it shows was computed, which is how you tell a stale row from a current one.

To bring one row forward, open the record, select the calculator image beside the value and select Recalculate. That needs write privileges on the table and Write on that row, runs in the form only, and refuses a row with more than 50,000 related rows or a hierarchy deeper than 10. The job's own Actions offer Resume, Postpone and Pause, so there is no way to run it sooner; schedule it into nonoperational hours instead.
