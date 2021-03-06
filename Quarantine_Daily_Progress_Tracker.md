## Daily progress tracker for V Predoi during Coronashit Quarantine
### Week 6-10 April 2020
- Monday, 6 April:
  - looked into Thibault netcdf-c + netcdf-py (for parallel write) env issue;
  - installed anaconda and esmvalcore/tool on home machine;
  - updated environments on Jasmin;
  - fixed a couple tests (one for core and one for tool);
  - opened two PRs for those;
  - debugged and identified concatenation issue (MWJury, iris and esmvalcore).
- Tuesday, 7 April:
  - Fixed esmvaltool environment with netcdf4 for parallel write
  - Cleaned up esmvaltool environment, tested and opened PR
  - Got ICL covid19 code and played a bit with it
  - Created environment and env script for ICL covid19 code for Jasmin
  - Went grocery shopping
- Wednesday, 8 April:
  - installed and created envs for covid19 model on Jasmin (v0.1.0)
  - tested it with Grenville
  - fixed a couple PRs in esmvaltool
  - fixed a couple cdds run params for Jonny
  - opened iris issue about netcdf parallel write
- Tuesday, 14 April:
  - installed covid=030 on Jasmin;
  - fixed a bunch of comments for an fx PR in ESMValTool
  - CMIP6 Archer call + fix a few run params for Jonny;
  - set up Prepare Deactivate documentation
- Wednesday, 15 April:
  - test esmvaltool environment
  - checked ESMValTool part2 paper
  - call with Ranjini and Lee talk about upcoming esmvaltool tutorial
- Thursday, 16 April:
  - reviewed monster diagnostic from Klaus
  - implemented flexible concatenation with overlaps in ESMValCore
- Monday, 20 April:
  - looked into and fixed bug preventing Jonny running cdds
  - fixed volume stats to handle masked arrays (esmvalcore)
  - written test and fixed cmorization testing module (esmvaltool)
  - added config user paths for Jasmin (esmvalcore)
  - attended CMIP6 poster sessions (2h, part 1)
- Tuesday, 21 April:
  - attended CMIP6 rehearsal and poster sessions and gave talk;
  - fixed volume stats again for nans
- Wednesday, 22 April:
  - birthday, general lax
  - attended UKESM core group meeting and UKESM weekly seminar
- Thursday, 23 April:
  - few preparations for tomorrow ESMValTool Tutorial
  - implemented a fix for computation of variable ctotal(cSoil, cVeg)
  - general cleanup in esmvaltool/core issues
  - fixed an isue abt installing esmvalcore on OSX
- Friday, 24 April:
  - esmvaltool virt tutorial
- Monday, 27 April:
  - Installed covid070
  - updated install instructions for esmvaltool
  - found issue with filing tests (flake8)
  - pinned flake8 in core and tool
- Tuesday, 28 April:
  - filled out Security Clear forms and sent to MO
  - fixed a whole lot of comments from Bouwe in a bunch of PRs
  - took CMIP6-Archer call
  - overhauled the overhaul of concatenation (better streamlined) and tested
  - wrote extra test for above item
- Wedensday, 29 April:
  - created modules for covid on Jasmin
  - fixed a few comments PRs in esmvaltool
  - went food shopping
  - wrote a vars/OBS data table in Earth System Model Evaluation Tool (ESMValTool) v2.0 – extended set of large-scale diagnostics for quasi-operational and comprehensive evaluation of Earth system models in CMIP (esmvaltool paper part 2) - bloody long and tedious table!
- Thursday, 30 April:
  - fixed long lasting issue with NE files shape selection
  - found a bug and fixed while in that process
  - 2 x PRs
  - made the covid modules more secure at Grenville suggestion (no more module load
    from module script)
- Monday, 11 May
  - ESMValTool tutorial (16 people, virtual)
- Tuesday, 12 May
  - Work on Ed Hawkins ACSIS branch in ESMValTool
