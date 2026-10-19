---
title: "Your model still fails to load after you enable the large storage format"
summary: "Large storage format lifts the SKU ceiling on a model's compressed size, but the capacity's Max Offline Semantic model Size still caps it in either format."
surface: power-bi
tip_number: 20
wave: "n/a - a capacity setting and a storage format, not a release wave"
build: "none - no CLI build involved; two Learn pages fetched and the SKU ceiling table parsed from one of them"
date: 2026-10-19
verified_on: 2026-10-19
verified_env: "Linux (CachyOS); two Learn pages fetched, canonical links matched and nine quoted sentences checked the same day; the SKU ceiling table parsed from the page and every row compared; no tenant, no capacity, no model"
expires_on: 2027-04-20
cost: "Premium or Fabric capacity (F or P SKU); the storage format and the capacity setting carry no per-model licence of their own"
source: "https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-admin-premium-workloads"
artifact: "assets/tips/20-large-format-does-not-lift-the-capacity-limit/check-size-limits.py"
evidence: |
  run 2026-10-19. Documentation-sourced tip: the two limits and the fix are each quoted from a vendor
  page, and nothing was executed against a capacity - there is no tenant on this machine. The artifact
  re-checks both halves that can be checked: the SKU ceiling table, parsed out of the page and compared
  row by row, and whether every sentence quoted below is still on the page it is attributed to.

  re-runnable: PYTHONDONTWRITEBYTECODE=1 python3 assets/tips/20-large-format-does-not-lift-the-capacity-limit/check-size-limits.py

  observed:
    SKU hard ceiling, small storage format only (13 rows parsed)
      F2               1 GB
      F4               2 GB
      F8/EM1/A1        3 GB
      F16/EM2/A2       5 GB
      F32/EM3/A3       6 GB
      F64/P1/A4       10 GB
      F128/P2/A5      10 GB
      F256/P3/A6      10 GB
      F512/P4/A7      10 GB
      F1024/P5/A8     10 GB
      F2048           10 GB
      F4096           10 GB
      F8192           10 GB
    rows matching the evidence block: 13/13
    caption present: 'Hard ceiling for Max Offline Semantic model size (small storage format).' -> True
    page: https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-admin-premium-workloads
      page text 13218 chars after tag strip, canonical matches
      quotes present: 5/5
    page: https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-large-models
      page text 9792 chars after tag strip, canonical matches
      quotes present: 4/4
    result: table and quotes both reproduce the evidence block
  exit 0

  `source:` carries one URL because validate_tips.py requires a single http(s) URL. The second page the
  body relies on is https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-large-models,
  which the artifact fetches and reports in the run above.

  Quoted sentences, page by page, in page order. Every one is matched by that run, ignoring tags,
  punctuation and whitespace.

  service-admin-premium-workloads, the Max Offline Semantic model Size setting:
    "The default value is 0, which is the highest limit defined by SKU."
    "The allowable range is between 0 and the capacity size limit."
    "This setting is applicable for models in both small semantic model storage format (ABF format) and large semantic model storage format (PremiumFiles), although the offline size of the same model might differ when stored in one format vs another."
    "If you have an existing semantic model that is larger than the size you specify for this setting, the semantic model will fail to load when a user tries to access it."
    "The additional SKU-specific hard ceiling in the below table does not apply to Power BI semantic models stored in large semantic model storage format."

  service-premium-large-models, the format and the steps, which is what makes the toggle look like the fix:
    "The default size limit is 1 GB."
    "While required for semantic models to grow beyond 10 GB, enabling the Large semantic model storage format has other benefits."
    "For Pro workspaces assigned to the Reserved Capacity for Pro Workspaces , the semantic model size limit is 1 GB."
    "expand Large semantic model storage format , set the slider to On , and then select Apply ."

  The two pages split the mechanism and the tip is the seam: the large-model page presents the toggle
  as the way past the size limit and names the capacity administrator's maximum only in passing, while
  the workloads page says that setting applies in both formats and its SKU ceiling applies in only one.
  The body claims nothing about a live capacity.
---

A semantic model outgrows its size limit. You set Large semantic model storage format to On in its Settings, refresh, and a reader still reports that the model failed to load. The capacity has memory free, and the setting is on.

The toggle changes how the model is stored. It also takes that model out from under the SKU ceiling for small-format models, which is 1 GB at F2, 6 GB at F32 and 10 GB at F64, and that ceiling does not apply to models stored in large format. What the toggle does not lift is the ceiling an administrator set on the capacity. Max Offline Semantic model Size, in the capacity's Semantic models workload, is the maximum compressed size of any one model there, and it applies in both formats. Pinned at 4 GB it stops a large-format model at 4 GB, and a model larger than the pinned value fails to load when a user tries to access it.

Read the capacity setting first: in OneLake catalog, Govern, Capacities, expand Workloads and find Max Offline Semantic model Size under Semantic models. A value of 0 means the highest limit the SKU defines, which for a large-format model is the capacity size; any other value caps models in either format and cannot lift a small-format model past the SKU ceiling. Set it, apply it, then set Large semantic model storage format to On in the model's Settings and apply. A model under that limit can still fail to load when it is larger than the Max Memory configured for the workload.
