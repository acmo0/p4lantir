# Contributing guidelines

**All contributions are welcome**, you can contribute in many ways :
- Open issues to report a bug or a feature request,
- Writing tutorials, blog posts, examples,
- Fixing typos or documentation,
- Writing new code to improve the project.

> If you encounter issues or get stuck while contributing, please feel free to an issue.

## Reporting a bug
Find the Issues tab on the top of the GitHub repository and click New Issue. You'll be prompted to choose between different types of issues, like bug reports and feature requests. Choose the one that best matches your need. The Issue will be populated with one of our templates. Please try to fillout the template with as much detail as you can. Remember: the more information we have, the easier it will be for us to solve your problem.

## Fixing a bug
You can choose to tackle any open issue in the issue tab of the project. See [code contribution](#code-contribution) section of this document for instructions about it.

## Feature request
Similarly to [bug reporting](#reporting-a-bug), feel free to open a new issue with the feature-request tag.

## Typos
If you encounter typos, please feel free to open an issue or correct it yourself and open a pull request as described in [general guidelines](#general-guidelines) section.

## Code contribution
### General guidelines

We follow the [git pull request workflow](http://www.asmeurer.com/git-workflow/) to
make changes to our codebase.
Every change made goes through a pull request,
this way, the *main* branch is always stable.

General guidelines for pull requests (PRs):

* **Open an issue first** describing what you want to do. If there is already an issue
  that matches your PR, leave a comment there instead to let us know what you plan to
  do.
* Each pull request should consist of a **small** and logical collection of changes.
* Larger changes should be broken down into smaller components and integrated
  separately.
* Bug fixes should be submitted in separate PRs.
* Describe what your PR changes and *why* this is a good thing. Be as specific as you
  can. The PR description is how we keep track of the changes made to the project over
  time.
* Do not commit changes to files that are irrelevant to your feature or bugfix (eg:
  `.gitignore`, IDE project files, etc).
* Write descriptive commit messages. Chris Beams has written a
  [guide](https://chris.beams.io/posts/git-commit/) on how to write good commit
  messages.
* Be willing to accept criticism and work on improving your code; we don't want to break
  other users' code, so care must be taken not to introduce bugs.
* Be aware that the pull request review process is not immediate, and is generally
  proportional to the size of the pull request.

### Setup
- Install system dependencies (see *Installation* section of [README.md](./README.md)),
- Clone/fork the project according to [https://www.asmeurer.com/git-workflow/](https://www.asmeurer.com/git-workflow/),
- Create a [python3 virtual environment](https://docs.python.org/3/library/venv.html),
- Install dev dependencies
```bash
# (with venv activated)
pip install -r requirements-dev.txt
```
- To test your fork :
```bash
python3 -m src.p4lantir [YOUR OPTIONS]
```

### Review
To merge a pull request, a review of a maintainer is required.