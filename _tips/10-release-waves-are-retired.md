---
title: "Release waves are over, and your repository still speaks wave"
summary: "The twice-yearly release wave is gone in favour of one always-on roadmap, so every reference you named after a wave has stopped being maintained."
surface: cross-cutting
tip_number: 10
wave: "n/a - retired in September 2026; disclosure is continuous on the AI at Work roadmap"
build: "Microsoft's 25 August 2026 announcement; the AI at Work roadmap and Release Planner as served on 2026-10-09"
date: 2026-10-10
verified_on: 2026-10-10
verified_env: "Linux, Python 3.14.7 - network fetch of the two public sources and three live roadmap URLs; no environment, no login"
expires_on: 2026-12-31
cost: "Free - the roadmap and Message Center are included; Message Center needs an admin role"
source: "https://www.microsoft.com/en-us/dynamics-365/blog/business-leader/2026/08/25/one-always-on-roadmap-dynamics-365-power-platform-and-dataverse-join-the-ai-at-work-roadmap/"
artifact: "assets/tips/10-release-waves-are-retired/wave-refs.py"
evidence: |
  command: curl -sSL -o ms.html <the announcement URL> && pandoc -f html -t plain ms.html
  observed: |
    200, 275203 bytes. The announcement, and the lines this tip turns on:
      "Starting in September 2026, Dynamics 365, Microsoft Power Platform, and Microsoft Dataverse
       roadmap content is joining the AI at Work roadmap"
      "We're retiring the twice-yearly release wave 1 and release wave 2 model"
      "Once published, each roadmap item remains current as it progresses through In Development,
       Rolling Out, and Launched"
      "By November 15, 2026  The transition completes and Release Planner retires"
      "Message Center remains the source for tenant-relevant change notifications"
      milestones table: September 2026 new capability begins publishing; September-November 2026
      content with a public preview or GA date of 1 June 2026 or later transitions
      Q. Will there be a September 2026 release wave 2 announcement or release wave 2 release plan?
      A. No.
      the roadmap's own affordances, quoted: "Filter roadmap views to the products that matter
      most", "Export complete or filtered roadmap views to a CSV file", "Subscribe to updates
      through RSS", "Search and organize roadmap content using feature IDs and advanced filters"

  command: curl -sSL -o iso.html <the Business Central article URL> && pandoc -f html -t plain iso.html
  observed: |
    200, 303335 bytes. Secondary source, and the one that answers the 2027 question:
      "No, there will not be a Dynamics 365 2027 release wave. As of September 2026, Dynamics 365 has
       transitioned to the always-on roadmap, AI at Work."
     (the article is written for Business Central; this tip stays with the CRM, Power Platform and
     Dataverse side of the change)

  command: for u in https://aka.ms/AIatWorkRoadmap https://releaseplans.microsoft.com/ https://learn.microsoft.com/en-us/dynamics365/release-plans/; do curl -sSL -o /dev/null -w '%{http_code} %{url_effective}\n' "$u"; done
  observed: |
    200 https://www.microsoft.com/en-au/microsoft-365/roadmap
    200 https://releaseplans.microsoft.com/en-US/
    200 https://learn.microsoft.com/en-us/dynamics365/release-plans/
    (all three still answering on 2026-10-09, so the November deadline is still ahead - the shortlink
    already resolves to the Microsoft 365 roadmap rather than to a release plan)

  command: python3 wave-refs.py /home/mozdemir/src/dataverse-solution-template
  exited: 0
  observed: |
    === /home/mozdemir/src/dataverse-solution-template ===
      nothing named after a wave

    no file named a wave

  command: python3 wave-refs.py <the repository, with this tip's own two files removed>
  exited: 1
  observed: |
    === /home/mozdemir/.hermes/cache/scratch/scan-target ===
      /home/mozdemir/.hermes/cache/scratch/scan-target/CONTRIBUTING.md
        line 31    wave 1 or wave 2                              wave: "2026 wave 1"
      /home/mozdemir/.hermes/cache/scratch/scan-target/_tips/1-read-a-solution-package-offline.md
        line 7     release wave                                  wave: "n/a - file format only; release waves were retired in September 2026"
      /home/mozdemir/.hermes/cache/scratch/scan-target/_tips/9-twelve-columns-you-did-not-create.md
        line 7     release wave                                  wave: "n/a - solution package format; release waves were retired in September 2026"
      /home/mozdemir/.hermes/cache/scratch/scan-target/queue/README.md
        line 3     release wave                                  A day with nothing worth publishing is normal: the change feed is thin between release waves, an
        line 19    wave 1 or wave 2                              Lake semantics - keep for a year. Feature tips ("what wave 1 added to X") rot in weeks. The
        line 21    wave 1 or wave 2                              5. **Expect the season.** Power Platform ships two waves a year - wave 1 GA in April, wave 2 GA 
        line 24    a release plan                                6. **The change feed is not the release plans.** Release plans stopped publishing in September 2
      /home/mozdemir/.hermes/cache/scratch/scan-target/queue/TEMPLATE.md
        line 28    release wave                                  expires_on: 2026-07-01      # no further out than one release wave
      /home/mozdemir/.hermes/cache/scratch/scan-target/scripts/test_gates.sh
        line 77    wave 1 or wave 2                              wave: "2026 wave 1"
        line 102   wave 1 or wave 2                              wave: "2026 wave 1"
        line 153   release wave                                  expect "expiry beyond one release wave is rejected" 1 "over the" "$DOC"
        line 286   wave 1 or wave 2                              wave: "2026 wave 1"
        line 303   wave 1 or wave 2                              wave: "2026 wave 1"
      /home/mozdemir/.hermes/cache/scratch/scan-target/scripts/validate_tips.py
        line 140   release wave                                  MAX_WINDOW_DAYS = 183  # one release wave
        line 372   release wave                                  f"{MAX_WINDOW_DAYS}-day cap (one release wave)"
    
    7 file(s) still name a wave, 15 reference(s) in total
    none of it will ever be refreshed again - the roadmap is continuous now
    (the whole output, pasted as printed on 2026-10-10, the day this tip went up. The tip's own
    two files are removed from the copy it scans, because this tip's text is itself full of the
    vocabulary - without that, the scan reads back its own transcript and the figure changes
    every time the tip is edited, which is why the body quotes no total)

---

Microsoft retired the twice-yearly release wave in September 2026. Dynamics 365, Power Platform and
Dataverse roadmap content now publishes to the AI at Work roadmap, where each item carries In Development,
Rolling Out or Launched and stays current as it moves between them, instead of arriving with a wave number
and a date. Release Planner retires by 15 November 2026, and there is no 2027 wave to wait for.

## Anything you named after a wave has stopped being maintained

Wave-era names stop being true without breaking anything. A board column still works, a pipeline parameter
still runs, a wiki page still loads, and every one of them says something that is no longer the case. Search
your repositories and documentation for `release wave`, `wave 1`, `RW1` and `release plan`.

## Set your own planning dates

A wave gave every organisation the same two dates a year to gather stakeholders and set a delivery window.
The roadmap is continuous, and it has filters, CSV export, RSS and stable feature IDs if you want to build a
view around it, so put the habit in the calendar yourself.

Message Center has not changed, and it is still the record for your own tenant: the roadmap says what is
coming, Message Center says what has reached yours.

## A board column will outlive the thing it is named after

Release Planner is going. Export anything you still need from it, then replace release-plan links in your
docs, pipeline comments and onboarding notes with links to the roadmap. Start with the bookmarked release
plans and the pinned "wave 1" boards.
