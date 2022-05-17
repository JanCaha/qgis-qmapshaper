# Changelog

## version 0.6

- allow partial generalization of layer based on selection for GUI tool and based on attribute value for processing tool

- add parameter to clean data in simplify tools (both processing and gui based ones)

- add tool to simplify inner or outer lines of polygon layers

- reworked the way how **mapshaper** folder is guessed 

- added option to specify command name to be runned in the Options - processing -> Providers

## version 0.5.1

- fix wrong import in utils.py causing an error

## version 0.5

- plugin is no longer experimental

- better mapshaper location identification, now based on existence system presence of `npm`

- GUI tests that caused issue on Github Actions are now skipped on Github Actions

## version 0.4

- use QProcess instead of Python's subprocess

- add planar option to tool Simplify Vector and Interactive Simplifier, that is determined by input layer CRS

- add tool - Convert to TopoJSON

- website
  
- add more tests to make plugin more robust
  

## version 0.3

- first version