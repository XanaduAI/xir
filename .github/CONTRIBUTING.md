# Contributing to XIR

Thank you for taking the time to contribute to XIR!
:confetti_ball: :tada: :fireworks: :balloon:

XIR is a collaborative effort with the quantum computation community - while we
will continue working on adding new and exciting features to XIR, we invite you
to join us and suggest improvements, research ideas, or even just to discuss how
XIR fits into your workflow.

## How can I get involved in the community?

If you want to contribute but don't know where to start, check out our
[documentation](https://quantum-xir.readthedocs.io) and have a go at working
through some of the tutorials.  Afterwards, take a look at the XIR package to
see how things work under the hood.

## How can I contribute?

It's up to you!

* **Be a part of our community** - provide exciting updates of the projects or
  experiments you are investigating with XIR.

  You can even write your own XIR tutorials, or blog about your XIR libraries.
  Send us the link, and we may even add it to our documentation as an external
  resource!

* **Test the cutting-edge XIR releases** - clone our GitHub repository, and keep
  up to date with the latest features. If you run into any bugs, make a bug
  report on our [issue tracker](https://github.com/XanaduAI/xir/issues).

* **Report bugs** - even if you are not using the development branch of XIR, if
  you come across any bugs or issues, make a bug report. See the next section
  for more details on the bug reporting procedure.

* **Suggest new features and enhancements** - use the GitHub issue tracker and
  let us know what will make XIR even better for your workflow.

* **Contribute to our documentation, or to XIR directly** - we are hoping for
  our documentation to become an online, open-source resource for all things
  quantum serialization. If you would like to add to it, or suggest
  improvements/changes, let us know - or even submit a pull request directly.
  All authors who have contributed to the XIR codebase will be listed alongside
  the latest release.

* **Build an application on top of XIR** - have an idea for an application, and
  XIR provides the perfect computational backbone? Consider making a fully
  separate app that builds upon XIR as a base. Ask us if you have any questions,
  and send a link to your application to support@xanadu.ai so we can highlight
  it in our documentation!

Appetite whetted? Keep reading below for all the nitty-gritty on reporting bugs,
contributing to the documentation, and submitting pull requests.

## Reporting bugs

We use the [GitHub issue tracker](https://github.com/XanaduAI/xir/issues) to
keep track of all reported bugs and issues. If you find a bug, or have an issue
with XIR, please submit a bug report! User reports help us make XIR better on
all fronts.

To submit a bug report, please work your way through the following checklist:

* **Search the issue tracker to make sure the bug wasn't previously reported**.
  If it was, you can add a comment to expand on the issue and share your
  experience.

* **Fill out the issue template**. If you cannot find an existing issue
  addressing the problem, create a new issue by filling out the
  [bug issue template](ISSUE_TEMPLATE/bug-report.yml). This template is added
  automatically to the comment box when you create a new issue. Please try and
  add as many details as possible!

* Try and make your issue as **clear, concise, and descriptive** as possible.
  Include a clear and descriptive title, and include all code snippets and
  commands required to reproduce the problem. If you're not sure what caused the
  issue, describe what you were doing when the issue occurred.

## Suggesting features, document additions, and enhancements

To suggest features and enhancements, use the
[feature request template](ISSUE_TEMPLATE/feature-request.yml). Be sure to:

* **Use a clear and descriptive title**

* **Provide a step-by-step description of the suggested feature**.

  - If the feature is related to any theoretical results in quantum computation,
    provide any relevant equations. Alternatively, provide references to
    papers or preprints with the relevant sections and equations noted.
  - If the feature is workflow-related, or related to the use of XIR, explain
    why the enhancement would be useful and where/how you would like to use it.

* **For documentation additions**, point us towards any relevant equations,
    papers, and preprints with the relevant sections and equations noted. Short
    descriptions of its use and importance would also be helpful.

## Pull requests

If you would like to contribute directly to the XIR codebase, simply make a
fork of the main branch and submit a
[pull request](https://help.github.com/articles/about-pull-requests). We
encourage everyone to have a go forking and modifying the XIR source code;
however, we have a couple of guidelines on pull requests to ensure the main
branch conforms to existing standards and quality.

### General guidelines

* **Do not make a pull request for minor typos/cosmetic code changes** - create
  an issue instead.
* **For major features, consider making an independent application** that runs
  on top of XIR, rather than modifying XIR directly.

### Before submitting

Before submitting a pull request, please make sure the following is done:

* **All new features must include a unit test.** If you've fixed a bug or added
  code that should be tested, add a test to the [`tests/`](tests/) directory!
* **All new classes, functions, and members must be clearly commented and documented**.
  If you do make documentation changes, make sure that the docs build and render
  correctly by running `make docs`.
* **Ensure that the test suite passes.**  Verify that `make test` passes.
* **Ensure that the modified code is formatted correctly.**  Verify that
  `make format` passes.

### Submitting the pull request
* When ready, submit your fork as a
  [pull request](https://help.github.com/articles/about-pull-requests) to the
  XIR repository, filling out the
  [pull request template](./PULL_REQUEST_TEMPLATE.md). This template is added
  automatically to the comment box when you create a new PR.

* When describing the pull request, please include as much detail as possible
  regarding the changes made, new features, and performance improvements. If
  including any bug fixes, mention the issue numbers associated with the bugs.

* Once you have submitted the pull request, two things will automatically occur:

  - The **test suite** will automatically run on
    [GitHub Actions](https://github.com/XanaduAI/xir/actions) to ensure
    that all tests continue to pass.

  - The **formatter** will automatically run on
    [GitHub Actions](https://github.com/XanaduAI/xir/actions) to ensure
    that all the code is properly formatted.

  Based on these results, we may ask you to make small changes to your branch
  before merging the pull request into the main branch. Alternatively, you can
  [grant us permission to make changes to your pull request branch](https://help.github.com/articles/allowing-changes-to-a-pull-request-branch-created-from-a-fork/).

Thank you for contributing to XIR!

\- The XIR team
