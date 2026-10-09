---
title: "Release waves are over, and your repository still speaks wave"
summary: "The twice-yearly release wave is gone in favour of one always-on roadmap, so every reference you named after a wave has stopped being maintained."
surface: cross-cutting
tip_number: 10
state: ready
next_step: ""
wave: "n/a - retired in September 2026; disclosure is continuous on the AI at Work roadmap"
build: "Microsoft's 25 August 2026 announcement; the AI at Work roadmap and Release Planner as served on 2026-10-09"
verified_on: 2026-10-09
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
  observed: |
    === /home/mozdemir/src/dataverse-solution-template ===
      nothing named after a wave

    no file named a wave
    exit: 0

  command: python3 wave-refs.py /home/mozdemir/src/makertipoftheday
  observed: |
    9 file(s) still name a wave, 43 reference(s) in total
    exit: 1
    files: assets/tips/10-release-waves-are-retired/wave-refs.py, CONTRIBUTING.md,
    _tips/1-read-a-solution-package-offline.md, _tips/9-twelve-columns-you-did-not-create.md,
    queue/10-release-waves-are-retired.md, queue/README.md, queue/TEMPLATE.md,
    scripts/test_gates.sh, scripts/validate_tips.py
    sample lines it printed:
      queue/TEMPLATE.md
        line 28    release wave        expires_on: 2026-07-01   # no further out than one release wave
      scripts/test_gates.sh
        line 77    wave 1 or wave 2   wave: "2026 wave 1"
      scripts/validate_tips.py
        line 140   release wave        MAX_WINDOW_DAYS = 183  # one release wave
    (taken on 2026-10-09 with the repository as it stood; the total moves as files change, because this
    tip's own body and evidence carry the vocabulary too - which is why the body quotes no figure)

---

Microsoft retired the twice-yearly release wave in September 2026. Dynamics 365, Power Platform and
Dataverse roadmap content now publishes to the AI at Work roadmap, where each item carries In Development,
Rolling Out or Launched and stays current as it moves between them, instead of arriving with a wave number
and a date. Release Planner retires by 15 November 2026, and there is no 2027 wave to wait for.

## Anything you named after a wave has stopped being maintained

Waves were not only a publishing cadence. They became words - a board column, a pipeline parameter, a wiki
page, a folder of release notes. Those names keep working and will never be updated again, which is harder
to notice than a broken link.

I scanned this repository for that vocabulary and it is in the repository's own docs, its queue templates
and its validator: `MAX_WINDOW_DAYS = 183  # one release wave`, `wave: "2026 wave 1"` in test fixtures, a
note promising an expiry "no further out than one release wave". Every one of them was accurate when it was
written, and not one of them can be checked against anything now. A solution template I had locally came
back clean, so this is not universal - it is the kind of thing you have to go looking for.

## The twice-a-year planning moment is yours to choose

A wave gave every organisation the same two dates a year to gather stakeholders and plan a window. Nothing
replaces that automatically. The roadmap gives you filters, CSV export, RSS per filtered view and stable
feature IDs, and it is continuous - so put a review rhythm in the calendar yourself, or the planning window
quietly disappears.

Message Center is unchanged, and for your tenant it is still the one that matters: the roadmap tells you
what is coming, Message Center tells you what has already been switched on in your environment.

## What to move before November

Release Planner is going. Export anything you still need from it, then replace release-plan links in your
docs, pipeline comments and onboarding notes with links to the roadmap. Bookmarked release plans and pinned
"wave 1" boards are the two places I would look first.
