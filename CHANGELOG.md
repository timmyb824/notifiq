# CHANGELOG

<!-- version list -->

## v1.8.0 (2025-07-03)

### Features

- Update pre-commit hooks to use newer versions and add option to override Gotify app token
  ([`90a0dee`](https://github.com/timmyb824/notifiq/commit/90a0deee2399330e96d7e5c78af220db8fe819e6))


## v1.7.1 (2025-06-23)

### Refactoring

- Conditionally refresh ArgoCD app only when using latest tag
  ([`cda19ba`](https://github.com/timmyb824/notifiq/commit/cda19bacd448d4ef8bccc740fc32fb40b1c07a56))


## v1.7.0 (2025-06-23)

### Features

- Add markdown formatting to Gotify notifications and update environment variables
  ([`9e12540`](https://github.com/timmyb824/notifiq/commit/9e125401e1f1930b02601a31d068424a088321fa))


## v1.6.2 (2025-06-22)

### Refactoring

- Remove unused Loki URL configuration and update environment variables
  ([`2860464`](https://github.com/timmyb824/notifiq/commit/286046411178cda823df7892692beaf5612e5c74))


## v1.6.1 (2025-06-22)

### Refactoring

- Convert priority mappings from integers to strings and improve URL transformation logic
  ([`da0bb6d`](https://github.com/timmyb824/notifiq/commit/da0bb6d13c5b9cdcd81dc9ec4283c0c9f589d41b))


## v1.6.0 (2025-06-22)

### Features

- Add priority support for Gotify and ntfy notifications
  ([`92f2025`](https://github.com/timmyb824/notifiq/commit/92f2025110d527e9e6ae092cde35e2630bd777f1))


## v1.5.3 (2025-06-20)

### Refactoring

- Remove Loki notifier and add Gotify support with dynamic app token override
  ([`2479f3c`](https://github.com/timmyb824/notifiq/commit/2479f3c9970fe53745a206ae82850cc8321be93c))

- Remove Loki notifier and add Gotify support with dynamic app token override
  ([`c84e6bc`](https://github.com/timmyb824/notifiq/commit/c84e6bcb2dc6ca92033328d6f76e15397e25ab28))


## v1.5.2 (2025-06-20)

### Documentation

- Add workflow guide for version and release process
  ([`8ff0694`](https://github.com/timmyb824/notifiq/commit/8ff0694fc1567dc9a247016f11907eb3dddc033e))


## v1.5.1 (2025-06-20)

### Bug Fixes

- Swap argument order in deploy script and add workflow doc template
  ([`de3ed02`](https://github.com/timmyb824/notifiq/commit/de3ed02576da0078a86cd3f2bebcdc03ae0050d5))


## v1.5.0 (2025-06-20)

### Features

- Allow custom tag parameter in deploy script
  ([`118dcbd`](https://github.com/timmyb824/notifiq/commit/118dcbd225fd2f2672bb74ecc4f03a3002328a0b))


## v1.4.1 (2025-06-20)

### Refactoring

- Dynamically build apprise URLs from environment variables instead of hardcoding providers
  ([`85f5b4e`](https://github.com/timmyb824/notifiq/commit/85f5b4e451f5ca8fc75c60b65f7cfaa363898f6e))


## v1.4.0 (2025-06-19)

### Features

- Add Gotify notification support and update dependencies
  ([`3289522`](https://github.com/timmyb824/notifiq/commit/328952246b49850c58796dfb53ff8efed43ac68b))


## v1.3.0 (2025-06-07)

### Features

- Add prometheus metrics for counts and response time
  ([`2f3d847`](https://github.com/timmyb824/notifiq/commit/2f3d8473e2483655654a888226c2bfa32c4676ca))


## v1.2.12 (2025-06-04)

### Refactoring

- Use httpx instead of requests in pursuit of emoji support
  ([`e471c7d`](https://github.com/timmyb824/notifiq/commit/e471c7d12336efcf383ee45843ceca966b3f8217))


## v1.2.11 (2025-06-04)

### Code Style

- Black formatting changes
  ([`359aeb4`](https://github.com/timmyb824/notifiq/commit/359aeb42b9203a6a615690cbd606ec49a60284b7))


## v1.2.10 (2025-06-04)

### Code Style

- Black formatting changes
  ([`f50749b`](https://github.com/timmyb824/notifiq/commit/f50749bb59bf271a82e709f7f8c6a6cf60312685))


## v1.2.9 (2025-06-04)

### Code Style

- Use json dumps for the payload
  ([`7dc4813`](https://github.com/timmyb824/notifiq/commit/7dc48139bb24eb633c62bc4e2b3627c42bb1ac2e))


## v1.2.8 (2025-06-04)

### Code Style

- Add logging for debugging
  ([`3c9fdd8`](https://github.com/timmyb824/notifiq/commit/3c9fdd871d5855eca374749c7b68153de983427c))

- Attempt to send message correctly to apprise
  ([`b3fe010`](https://github.com/timmyb824/notifiq/commit/b3fe0100c4c3c055587a490ef108a0a7044463f5))

- Black formatting changes
  ([`b1baf88`](https://github.com/timmyb824/notifiq/commit/b1baf88c164a3348c3de432c8847a0fea63c0b6e))


## v1.2.7 (2025-06-04)

### Refactoring

- Simplify URL handling and topic determination logic in NtfyDirectNotifier clas
  ([`ccf8d63`](https://github.com/timmyb824/notifiq/commit/ccf8d63eb29fa272f6a15fb4cf16676bbc0e53bd))


## v1.2.6 (2025-06-04)

### Refactoring

- Ntfy direct to use the ntfy json api instead of /topic
  ([`9391eff`](https://github.com/timmyb824/notifiq/commit/9391effff0d7d275eddba17c9bf5b126bff6a33d))


## v1.2.5 (2025-06-04)

### Bug Fixes

- Fix encoding issue in request data assignment
  ([`ea6c516`](https://github.com/timmyb824/notifiq/commit/ea6c516d48e8023f1c88818b31e879577c554fda))


## v1.2.4 (2025-06-04)

### Code Style

- Add Content-Type to request headers in NtfyDirectNotifier class
  ([`0916774`](https://github.com/timmyb824/notifiq/commit/0916774d3e522f9a19b6be8048a7f9355ff175d9))


## v1.2.3 (2025-06-04)

### Code Style

- Add logging for ntfy-direct
  ([`528eb6f`](https://github.com/timmyb824/notifiq/commit/528eb6f6457492a43fae7591978d75aa9ffbae34))


## v1.2.2 (2025-06-04)

### Chores

- Change ntfy env in encrypted file
  ([`a190712`](https://github.com/timmyb824/notifiq/commit/a19071220f53222f9d7bf67dcbdf097a23668b19))

- Change ntfy env in encrypted file
  ([`abb2072`](https://github.com/timmyb824/notifiq/commit/abb20721f00866b9ffd526b140457b36a2bd00e1))

- Update pre-commit hook
  ([`332a5ed`](https://github.com/timmyb824/notifiq/commit/332a5ed81a6a13f1d2318cd2dafe983283042651))

- Update pre-commit hook
  ([`5a7991e`](https://github.com/timmyb824/notifiq/commit/5a7991e54f4899a891bb7d677ed2ca633fc31ad2))


## v1.2.1 (2025-06-04)

### Refactoring

- Update URL handling in NtfyDirectNotifier for topic override
  ([`2843166`](https://github.com/timmyb824/notifiq/commit/284316621b98eef302a7d78ddf9d5acd696989ec))


## v1.2.0 (2025-06-04)

### Code Style

- Add missing Any
  ([`941f723`](https://github.com/timmyb824/notifiq/commit/941f7234f783206030f201c4d44d02bd66c5e564))

### Features

- Implement ntfy direct using request instead of apprise to get markdown support
  ([`844600b`](https://github.com/timmyb824/notifiq/commit/844600bdb0edb7a77b3a25b8114e38453809c443))


## v1.1.4 (2025-06-03)

### Bug Fixes

- Ensure extra fields are passed through
  ([`517f7fb`](https://github.com/timmyb824/notifiq/commit/517f7fbbca5664dbf45175b9dbd2924e46c50758))


## v1.1.3 (2025-06-03)

### Chores

- Add missing env to envrc
  ([`d427255`](https://github.com/timmyb824/notifiq/commit/d4272554fc99618473505deabd5417be3229b81a))


## v1.1.2 (2025-06-03)

### Code Style

- Enable argocd actions in deploy script
  ([`f0d1b00`](https://github.com/timmyb824/notifiq/commit/f0d1b0030586ee1f02b4dbbbbc4933b4369e6810))


## v1.1.1 (2025-06-03)

### Chores

- Update mattermost env
  ([`a239a08`](https://github.com/timmyb824/notifiq/commit/a239a08f144746e2098ea38fbadb2a31881b2fbb))


## v1.1.0 (2025-06-03)

### Features

- Add support for dynamic urls for ntfy and mattermost
  ([`c69acf2`](https://github.com/timmyb824/notifiq/commit/c69acf225fa4e8a6793daf9370de7a6d1e5824b5))


## v1.0.0 (2025-06-02)

- Initial Release
