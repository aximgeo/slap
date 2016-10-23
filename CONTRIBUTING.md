## Getting Started

We welcome any contributions of code, tests, documentation, or feature and bug reports.  At a minimum, you'll need a [GitHub account](https://github.com/signup/free).  The general process will be something like:

* Create a new issue (or perhaps comment on an existing one, if you're having the same problem)
* Fork the repository
* Create a feature branch
* Submit a pull request

## Creating an Issue

* Create an [issue](https://github.com/gisinc/slap/issues), assuming one does not already exist.
  * Clearly describe the issue, including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.
* Fork the repository on GitHub

## Making Changes

* Create a feature branch from where you want to base your work (usually the `master` branch)
* Make commits of logical units.  In general, commits should be:
  * Granular - Don't try to do too much in a single commit
  * Relevant - If you run across another minor bug while working on an issue, please create a new issue and a new branch for your fix
  * Descriptive - Commit messages should be clear, well-formatted, and detailed
* Submit a [pull request](https://help.github.com/articles/creating-a-pull-request/)

## Tests and CI
* All new features should include tests as well
* If you are fixing a bug, please provide a test that would have caught the bug in the first place, if possible
* When you submit a pull request, the CI server will automatically run all the tests; before a pull request can be approved, all tests must pass
* To run the tests locally, you can use `python -m unittest discover tests`, or any other python test runner