---
title: "The heat map on a choice column has one colour for every option"
summary: "A heat map reads the number stored behind each choice against a 0-100 range, and option values start in the hundreds of millions, so every option lands at the same end."
surface: dataverse
tip_number: 21
wave: "n/a - a preview display option, not a release wave"
build: "none - no CLI build involved; one Learn page fetched and fifteen option-set files parsed from a public sample at a pinned commit"
date: 2026-10-20
verified_on: 2026-10-20
verified_env: "Linux (CachyOS); one Learn page fetched with its canonical link and four quoted sentences matched the same day; fifteen option-set XML files parsed from microsoft/Nonprofits at a pinned commit; no tenant, no Power Apps session, nothing rendered in a grid"
expires_on: 2027-04-21
cost: "No licence beyond the Power Apps environment; the visualization is a preview display option"
source: "https://learn.microsoft.com/en-us/power-apps/maker/data-platform/column-visualizations-grids"
artifact: "assets/tips/21-heat-map-on-a-choice-column/check-choice-values.py"
evidence: |
  run 2026-10-20. Mixed tip: the stored option values are measured from a public sample solution, and
  the range behaviour is quoted from the Learn page for the preview feature. Nothing was rendered in a
  grid - there is no tenant on this machine, so the claim about what every row shows is the documented
  rule applied to the measured values, not an observation of a screen.

  re-runnable: PYTHONDONTWRITEBYTECODE=1 python3 assets/tips/21-heat-map-on-a-choice-column/check-choice-values.py

  observed:
    microsoft/Nonprofits@e41c4afec718  option set files: 15
    option sets with options: 15
    sets where every value is outside 0-100: 15
    lowest stored value: 844060000   highest stored value: 863850003
    example, sifund_ccbrandcode.xml: 11 options
          844060000  Visa
          844060001  MasterCard
          844060002  Visa Debit
          844060003  MasterCard Debit
          844060004  American Express
          844060005  Diners Club
          844060006  JCB
          844060007  Interact
          844060008  Discover Card
          844060009  Union Pay
          844060010  Unknown
    numbers: reproduce the evidence block
    page: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/column-visualizations-grids
      page text 8583 chars after tag strip, canonical matches
      quotes present: 4/4
    result: numbers and quotes both reproduce the evidence block
  exit 0

  Quoted sentences, in page order. Every one is matched by that run, ignoring tags, punctuation and
  whitespace.

    "For choice (option set) columns, the numeric value behind the selected choice is used, and the choice's text is shown as the label."
    "By default, the range is 0 to 100, and the value's position in that range decides the color."
    "Values outside the range are pulled to the nearest end of the range (0 or 100 by default)."
    "For choice columns, the color follows the number assigned to each choice, which might not match the visible list order if those numbers aren't in low-to-high sequence."

  The page states the rule and the sample supplies the values; neither half alone is the tip. The
  page's own examples use values such as 12, 55 and 90, so the failure does not show up when you try
  a heat map on a number column and then move it to a choice.
---

The visualization dropdown on a column is tempting on a choice column. You set Heat Map on Priority, expecting Low to sit at one end of the colour range and High at the other, then open a view.

Every row shows the bar at the same end, in the same colour. The heat map reads the number stored behind the selected choice, not its position in the list, and reads it against a range of 0 to 100 by default. Custom options carry the publisher's prefix, so their stored values start in the hundreds of millions: across the fifteen option sets in one published Microsoft sample solution they run from 844060000 to 863850003. Every one of those is outside the range, values outside the range are pulled to the nearest end, and Low and High end up rendered identically.

Leave the choice column set to None. Add a whole number column scored 0 to 100, or a formula column that maps each choice to that score, and put the heat map on that column instead. The choice column stays as the label, and the bar starts meaning something.
