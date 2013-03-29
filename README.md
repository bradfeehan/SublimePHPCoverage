SublimePHPCoverage
==================

A plugin for Sublime Text 2, which visualises PHP code coverage data in
the editor.

## Installation

Put the SublimePHPCoverage folder in your
`~/Library/Application Support/Sublime Text 2/Packages` folder. You can
do this with git:

```bash
$ git clone git://github.com/bradfeehan/SublimePHPCoverage.git "~/Library/Application Support/Sublime Text 2/Packages/SublimePHPCoverage"
```


## Setting up PHPUnit

Make sure PHPUnit is configured to output code coverage data to
`tests/coverage/clover.xml` (relative to your Sublime Text 2 project
root), in Clover format. You can do this with PHPUnit's
[command-line arguments][1]:

```bash
~/myProject$ phpunit --coverage-clover tests/coverage/clover.xml
```

...or in PHPUnit's [XML configuration file][2]:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit>
	<!-- ... -->
	<logging>
		<log type="coverage-clover" target="tests/coverage/clover.xml" />
	</logging>
	<!-- ... -->
</phpunit>
```


## Usage

The code coverage data will be loaded from the Clover file and
displayed in the margin, with a summary in the status bar:

![Example](http://i.imgur.com/4ASco.png)

Green lines are covered, red are not covered, and non-annotated lines
aren't executable (not counted in code coverage data).

### Manually triggering a refresh

You can hit ⌘⇧C to trigger a refresh of the code coverage data for the
currently focused view (tab).

The pluginalse  adds an "phpcoverage_update" command, which can be
used to refresh the code coverage data for all open files. This command
can be called in a variety of ways, e.g. from the command line:

```bash
$ subl --command phpcoverage_update
```

This is handy to include after running PHPUnit in a script, as it'll
automatically refresh the information shown in Sublime with the new
code coverage (which is almost certainly what you want, at least until
I add some support for detecting changes to the code coverage file and
updating the display automatically... Pull Requests accepted!)


## Troubleshooting

Check the code coverage file is present and has a `<file>` element
for the file in question. Also look in Sublime's console (accessible
via <code>Ctrl + `</code>).

[1]: <http://www.phpunit.de/manual/current/en/textui.html#textui.clioptions> "PHPUnit Command-Line Switches"
[2]: <http://www.phpunit.de/manual/current/en/appendixes.configuration.html> "PHPUnit XML Configuration File"
