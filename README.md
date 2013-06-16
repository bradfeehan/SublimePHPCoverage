# SublimePHPCoverage Plugin

[![Build Status](https://travis-ci.org/bradfeehan/SublimePHPCoverage.png?branch=master)](https://travis-ci.org/bradfeehan/SublimePHPCoverage)

A plugin for Sublime Text 2, which visualises PHP code coverage data in
the editor. Test coverage data is parsed from a Clover coverage file,
and displayed visually in the margin, with a summary in the status bar.

![Example](http://i.imgur.com/4ASco.png)

Green (dot) lines are covered by at least one test, red (arrow) lines
are not covered, and non-annotated lines aren't executable, so are not
counted in code coverage data).

* Works with Sublime Text 2 or 3
* Tested on Mac OS X and Windows
* Automatically updates the display when new coverage data is available




## Installation

Before you start, the requirements are:

* Sublime Text 2 or 3
* [Package Control][1] (optional, recommended)
* PHP installed and set up with [Xdebug][2]
* A PHP project which is using PHPUnit for its test suite

[1]: <http://wbond.net/sublime_packages/package_control>
[2]: <http://xdebug.org/>

## Package Control

The simplest way to install the plugin is using Package Control.
Go to Preferences > Package Control > Install Package, type in
"PHP Coverage", and hit Enter. You're done! Check out the configuration
section.

## Manual Installation

If you're thinking of hacking on or contributing to the plugin, then
it's probably best to install the plugin manually. You'll want to get
this Git repository into your Sublime Text Packages folder. That will
be located in a variety of locations depending on your operating system
and Sublime Text version.

* Sublime Text 2
   * Windows: `%APPDATA%\Sublime Text 2\Packages`
   * OS X: `~/Library/Application Support/Sublime Text 2/Packages`
   * Linux: `~/.Sublime Text 2/Packages` (untested)
   * Portable Installation: `Sublime Text 2/Data/Packages` (untested)
* Sublime Text 3
   * Windows: `%APPDATA%\Sublime Text 3\Packages`
   * OS X: `~/Library/Application Support/Sublime Text 3/Packages`
   * Linux: `~/.Sublime Text 3/Packages` (untested)
   * Portable Installation: `Sublime Text 3/Data/Packages` (untested)

You can do this in one go using Git:

```bash
$ git clone git://github.com/bradfeehan/SublimePHPCoverage.git "~/Library/Application Support/Sublime Text 2/Packages/SublimePHPCoverage"
```




## Configuration

`SublimePHPCoverage.sublime-settings` contains a variety of
configuration options. These can all be overridden individually in the
user configuration file.

Additionally, settings may be set on a per-project basis in the
Sublime project file (e.g. `myProject.sublime-project`). This is
especially useful for setting the path to the Clover report, as it may
differ for each project.

To override a setting in a project, simply put the overridden settings
into a JSON object. Put that object in the `settings` section of your
Sublime project file, under a key with the name of `phpcoverage`. For
example, if you wanted to change the report path for a particular
project, your Sublime project file might look a little like this:

```json
{
    "folders": [
        {
            "path": "/path/to/project"
        }
    ],
    "settings": {
        "phpcoverage": {
            "report_path": "path/to/coverage.xml"
        }
    }
}
```

##### `debug` (boolean)

Default: `false`

When set to `true`, the plugin will provide detailed diagnostic logging
to the Sublime console (accessible via <code>Ctrl + `</code>).

If you're experiencing a reproducible issue with the plugin, please
enable this option and provide as much of this logging data as possible
in a bug report.

##### `report_path` (string)

Default: `build/logs/clover.xml`

This controls how the plugin finds coverage data for a given PHP source
file. When looking for the coverage data for a file, the plugin will
ascend upwards through the file's parent directories, until it finds a
file with this name (relative to one of the file's parent directories).

For example, if the plugin needs to find the file containing the
coverage data for `/path/to/my/project/foo/bar/baz.php`, and the
`report_path` is set to `abc/def/clover.xml`, then the plugin will look
for the coverage data file in the following locations:

1. /path/to/my/project/foo/bar/abc/def/clover.xml
2. /path/to/my/project/foo/abc/def/clover.xml
3. /path/to/my/project/abc/def/clover.xml
4. /path/to/my/abc/def/clover.xml
5. /path/to/abc/def/clover.xml
6. /path/abc/def/clover.xml

The plugin will stop at the first file in the above list which exists,
and that will be the file assumed to contain coverage data for
`baz.php`. If none of the files in the list above exist, or the first
one in the list which exists doesn't contain any coverage data for
`baz.php`, then the plugin will not show any coverage data in the
editor.

##### `watch_report` (boolean)

Default: `true`

If set to `true` (the default), when a PHP file is open in Sublime,
the plugin will spawn a "watcher" thread which monitors the relevant
coverage file for any changes. If the watcher detects any changes to
the coverage file, it will trigger an update of the displayed coverage
data in the editor.

Although the watcher thread uses polling to watch the file, it
shouldn't cause a significant amount of load while running in most
cases. However, if it does, you can try disabling the functionality
using this configuration option (and simply update the coverage data
manually).

##### `include` (array)

Default: `["\.php$"]`

This option (together with `exclude`, documented below) controls what
filenames will be considered PHP files for the purposes of showing the
coverage data in the editor. The default behaviour is to only enable
the plugin's functionality for files which end with `.php`.

It should be an array of strings, where each of the strings contains a
regular expression pattern. If any of the patterns in the array match
the filename, then the file will be included -- unless it also is
excluded by the `exclude` option below.

##### `exclude` (array)

Default: `["[/\\]tests?[/\\].*"]`

This option (together with `include`, documented above) controls what
filenames will be considered PHP files for the purposes of showing the
coverage data in the editor. The default behaviour is to disable the
plugin's functionality for files that reside in a folder named either
`test` or `tests` (the rationale is that your PHPUnit tests may reside
in a folder with one of these names, and they won't have any code
coverage data of their own).

It should be an array of strings, where each of the strings contains a
regular expression pattern. If any of the patterns in the array match
the filename, then the file will be excluded. This will force the
plugin to be disabled for that file, regardless of whether it was
included by the `include` option above.




## Setting up PHPUnit

PHPUnit should be configured to output code coverage data in Clover
format. The coverage data should be stored at the location referenced
by the `report_path` option (which defaults to `build/logs/clover.xml`).

This can be done with PHPUnit's [command-line arguments][3]:

```bash
~/myProject$ phpunit --coverage-clover build/logs/clover.xml
```

...or, preferably, in PHPUnit's [XML configuration file][2]:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit>
	<!-- ... -->
	<logging>
		<log type="coverage-clover" target="build/logs/clover.xml" />
	</logging>
	<!-- ... -->
</phpunit>
```

[3]: <http://www.phpunit.de/manual/current/en/textui.html#textui.clioptions> "PHPUnit Command-Line Switches"
[4]: <http://www.phpunit.de/manual/current/en/appendixes.configuration.html> "PHPUnit XML Configuration File"

#### Automatic Builds

This plugin previously featured a command which would execute PHPUnit,
generating the code coverage report automatically. However, this
functionality has been removed as of v0.2, as the same behaviour can
now be achieved using Sublime Text's built-in Build Systems feature.

To set this up, add something similar to the following section to your
Sublime project file (e.g. `myProject.sublime-project`):

```json
{
    "build_systems": [
        {
            "name": "PHPUnit",
            "working_dir": "$project_path",
            "cmd": [
                "vendor/bin/phpunit",
                "--coverage-clover",
                "build/logs/clover.xml"
            ]
        }
    ]
}
```

There will then be a new "PHPUnit" option in the Tools > Build System
menu. By selecting this, you can then use ⌘B to run your PHPUnit tests.




## Usage

Once your code coverage data file is in the right location, any PHP
files opened in Sublime should show code coverage data in the margin
and in the status bar.

#### Hands-Free Mode

When the code coverage data file is updated at the end of a PHPUnit
test run, if you have the `watch_report` setting enabled (the default),
the plugin will detect that the code coverage data file has been
updated, and it will update the code coverage data shown for any files
open in the editor.

#### Manually Triggering A Refresh

If there are issues with the automatic `watch_report` setting, it can
be disabled. In that case, the code coverage shown in the editor can be
manually refreshed. To do so, go to Tools > PHP Coverage > Update
Current File, or press ⌘⇧C.




## Troubleshooting

Check that the code coverage file is present, and in the correct
location (as referenced by the `report_path` setting).

Check also that the code coverage file has a `<file>` element for the
file in question.

Also consider enabling debug mode (using the `debug` setting), and look
in Sublime's console, accessible via <code>Ctrl + `</code>.

Please submit any further problems you might run into as GitHub issues.




## Contributing

I'd be interested to know about any changes people are making, and
any contributions are most welcome. Here's a couple of guidelines to
try and help the project stay at its best.

* Try to keep the code modular and testable where possible
* Try to add docstrings to everything, to explain its purpose
* Consider cross-platform issues, and Sublime 2 vs. 3 compatibility
* Use four spaces for each level of indentation
* Please keep code lines under 80 characters in length
* Please keep paragraphs in the README to 72 characters
