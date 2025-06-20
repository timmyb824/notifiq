---
description: Deploy with version and latest tags, handling pending changes safely
---

1. **Check for pending changes in the repository.**
   - If the only pending change is to `.envrc`, stash it using `git stash push`.
   - If there are changes to any other files, prompt the user to commit them and stop the workflow.
2. **If changes were stashed or there were no pending changes**, run `git pull` to fetch the latest updates from the remote repository.
3. **Run the deploy script with the `latest` tag:**
   - `./deploy.sh latest`
   - Wait for it to finish.
4. **Run the deploy script again using the version specified in `pyproject.toml`.**
5. **After both deployments complete successfully, restore the stashed `.envrc` changes with:**
   - `git stash pop`
