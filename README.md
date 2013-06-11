openshift_deploy
================

In case you need to move the app to another Openshift account or recreate it, here's what needs to be done (note that the app name has to stay the same through all the steps):

1. `rhc snapshot save <app_name> -f <output_file>`
2. log in to the other account or delete the existing app (`rhc app delete <app_name>`)
3. `rhc app create <app_name> python-2.6 --no-git`
4. `rhc snapshot restore <app_name> -f <app_backup_file>`
5. wait a while
6. get the git repo url: `rhc app show <app_name>`
7. `git clone <git_repo_url>`
