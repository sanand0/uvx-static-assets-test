# Prompts

## Test uvx with static assets

<!--
cd /home/sanand/code/infra/uvx-github
dev.sh
copilot --yolo --model gpt-5.4 --effort xhigh
-->

I want to test if it is possible to run a Python project directly from GitHub using this command.

`uvx --from "git+https://github.com/owner/repo.git@branch" script-name`

To do this, we would need to create a pyproject.toml. I specifically want to check if we can allow a script like this to access static assets. So let's try this scenario. Create a text template file, write a Python application that can run using `uvx`, and we'll, based on a command line argument, load the template and modify some parameters in the template and print the output. This will demonstrate that the program can, in fact, load the static assets relative to wherever it is installed using the `uvx` environment and be able to generate output accordingly, and that `uvx` will, in fact, copy all the files from that repo, not just that individual file and so on.

Run this, test it, proof that it works, document all your findings in a findings.md.

You can create a repo called `uvx-static-assets-test` from the current directory using the `gh` CLI tool, and then create the necessary files in that repo, commit and push them, and then run the `uvx` command to test if it works. Document all your findings in a `findings.md` file in the same repo.

(Commit and push prompts.md which I'm editing.)

---

Simplify this to the least amount of code and least number of files possible. Ideally, we would have:

- A single Python script, no more. Directly at the repo root, not under src/**. No tests.
- A single messages.txt at the repo root.
- .gitignore, pyproject.toml, uv.lock, findings.md, prompts.md are fine.

Simpify the Python script to the ABSOLUTELY smallest size possible. Maybe even just 10 lines. The aim is to show the smallest possible proof of concept.

Run, test and verify.
