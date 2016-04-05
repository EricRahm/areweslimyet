MozAreWeSlimYet
===============

Code behind areweslimyet.com

## Regression tracking

Regressions seen on areweslimyet.com should be filed on Mozilla's
Bugzilla instance, blocking [bug 1120576](https://bugzilla.mozilla.org/show_bug.cgi?id=1120576).

## How It works

### BenchTester

This provides BenchTester.py, a framework for running a bench test module, and
providing it a add_test_results callback that inserts tests into sqlite
databases it manages.

The MarionetteTest.py file is such a module, which launches a marionette
test, waits for the test to finish.

BuildGetter.py is a helper that has functions for scanning archive.mozilla.org for
available builds, and fetching them.

BatchTester.py is a runner for BenchTester that runs a long-lived daemon,
running multithreaded tests side-by-side. It requires a 'hook' file that
provides functions to turn test objects, represented by json blobs, into actual
commands that invoke a test.

BatchTester.py can read in test requests from a status directory, and write out
a status.json file. This is used by the areweslimyet.com/status/ page to both
queue and monitor running tests.

### The AreWeSlimYet test

The `benchtester` folder has a marionette test that is fairly simple:
- Open all 100 pages of TP5, into 30 tabs (re-using tabs round-robin style), on a timer.
- Close all the tabs.
- Repeat.
- At various points, call the memory reporter subsystem and fire an event with a
  memory snapshot as data that the MarionetteTest.py module will forward to the
  database.

`slimtest_config.py` holds the values we configure the endurance test
with. Sourced by run_slimtest.py and slimtest_batchtester_hook.py

`run_slimtest.py` uses BenchTester to load the MarionetteTest module with our
endurance test, and run it against a specific firefox build.

`slimtest_batchtester_hook.py` is a hook that the BatchTester.py daemon requires
to schedule our tests. It provides a function to take the requested tests --
JSON objects generated by e.g. /html/status/request.cgi -- and setup a
BenchTester run against them. This is effectively the daemonized version of
run_slimtest.py, used by the dedicated test machine. See
tester_scripts/launch_tester.sh for an example of usage.

`slimtest_linux.sh` is a wrapper around run_slimtest.py for spawning the TP5
pageset and a VNC session, then running a test in said session. Specifically,
it:
- Creates a VNC session
- Launches nginx against the $PWD/nginx/ prefix, assumed to hold the TP5 pageset
  needed by the endurance test. (See tester_scripts/tp5.nginx.conf for an
  example of setting this up)
- Invokes run_slimtest.py
- Cleans up VNC and nginx

(See "Running a SlimTest" below for a usage example.)

`create_graph_json.py` takes a BenchTester sqlite database that has results from
our endurance test(s), and generates a set of datapoints suitable for
graphing. The configuration for what datapoints to export is embedded at the
beginning of this script.

`merge_graph_json.py` takes a series of json files output by
create_graph_json.py of the form seriesname-a, seriesname-b, etc., and creates a
master 'seriesname.json' which holds a condensed view of the subseries, as well
as references to the subseries files. This is used by the website to store tests
in per-month databases, and then create a much smaller "master" file. The
website will then request the sub-series when the graph is zoomed in
sufficiently on one region.

### The website

The `html` folder holds the website currently hosted at
https://areweslimyet.com/. It expects the master file created by
merge_graph_json.py to be at `html/data/areweslimyet.json`, and the relevant
create_graph_json.py output to live alongside it.

`html/status/` reads the output of the BatchTester.py daemon and shows you what
it's up to.

`html/status/request.cgi` allows you to write to /status/batch/ to send requests
to the daemon. This script is not active on the public mirror for obvious
reasons.

`html/status/slimyet.js` holds most of the magic. Note that the configuration in
this file for what graphs to show must match the datapoints configured for
export in create_graph_json.py. The annotations that appear on the graph with
question marks are defined in this file.

### Running a SlimTest

 - Obtain the TP5 pageset, or a similar set of pages to use (though you'll need
 TP5 for results comparable to the official areweslimyet.com test)
 - Install marionette-client from pip (pip install 'marionette-client')
 - Install mercurial from pip (pip install 'mercurial')
 - The test takes almost two hours by default, so lets stuff it in a vnc session
   - `vncserver :9`
 - Start a local webserver for the TP5 pageset, which AWSY expects to be on
   localhost:8001 through localhost:8100
   - `nginx -C my_tp5_thing/nginx.conf`
   - To use a different (more public) pageset, edit
     `benchtester/test_memory_usage.py`'s TEST_SITES array to target the desired
     pages
 - Get a Firefox build to test, let's say it's ./firefox/
 - Pick a database to put this data in, lets say mytests.sqlite (it doesn't have
 to exist, BenchTester will create it)
 - Run it! `./run_slimtest.py --binary ./firefox/firefox --sqlite
   ./mytests.sqlite -l foo.log --buildname mytestbuild --buildtime $(date +%s
   --date="Jan 1 2014")`
   - buildname is the name of this build in the database
   - buildtime is its unix timestamp, used by the website as the x axis

Your results are in mytests.sqlite, use e.g. `sqliteman` to examine them, or see
"Generating the Website Data" below for using the areweslimyet website to
visualize them.

### Generating the Website Data

For the official test box we split up test databases by month into files named
db/areweslimyet-YYYY-MM.sqlite, which are fed to create_graph_json.py to create
html/data/areweslimyet-YYYY-MM.json.gz

merge_graph_data.py then creates html/data/areweslimyet.json.gz, the 'zoomed
out' master file. Note that this master file is required even if you only have
one sub-series of data (and the subseries do not need to be split by month,
you're welcome to have areweslimyet-all.sqlite as the only subseries)

This means, if you have a database named mytests.sqlite from "Running a
SlimTest" above, you would need to do the following:

    # Create mytests-main.json.gz with the full graph data for my series
    ./create_graph_json.py ./mytests.sqlite mytests-1 html/data/
    # (and optionally create mytests-2 mytests-3, etc)
    # Merge series into overview file mytests.json.gz (required even if you only
    # have one series)
    ./merge_graph_json.py mytests html/data/

That's it! Now view your data lives in html/data/. Note that you need a
webserver capable of serving .json.gz files transparently in order for the
javascript to request them from e.g. /html/data/foo.json. (Alternatively, simply
run `gzip -d` on the produced files, though be warned that they get quite large)
