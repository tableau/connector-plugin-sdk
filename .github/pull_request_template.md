**A Helpful Guide For Navigating Our Branches**

* If this is a hotfix, make your PR against `master`.
* If your change can ship immediately, make your PR against `dev`.
* If your change is for a future release, make your PR against the appropriate holding branch (eg `dev-2020.1`)

_Also:_
* Please update the changelog of the project you modified, either under `vNext` or under a point release if you bumped the version.
* If you are merging into master, update the root `README.md` if the PR includes a release of the SDK, Connector Packager, or TDVT.

Thank you and feel free to delete this from your PR description!
