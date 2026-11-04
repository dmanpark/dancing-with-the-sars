# Setup: Claude Code prompt

## How to use this

On the 3090 machine, open a terminal in `C:\Users\daria\PROJECT_DWTS`, start Claude Code, and say: **"Read prompts/setup.md and carry it out."** Windows PowerShell, Windows Terminal or an Ubuntu window all work; the prompt figures out where it is.

Claude Code sets up WSL2, the Linux copy of the repo, Python, the data folders and your Earthdata login, then starts the preliminary tests in [prelim-tests.md](prelim-tests.md) on its own.

**What only you can do.** Claude stops and tells you when each one comes up.

1. **Make a free NASA Earthdata account now**, if you don't have one: [urs.earthdata.nasa.gov/users/new](https://urs.earthdata.nasa.gov/users/new). It takes two minutes and needs your email confirmed.
2. If WSL2 isn't installed yet: run one command as administrator, then restart the PC.
3. The first time Ubuntu opens: pick a Linux username and password.
4. Type your Earthdata username and password into a small window Claude opens. Claude never sees them.
5. The first time Claude Code starts inside Ubuntu: log in to Claude.

---

## Your job

Set up this machine so `prompts/prelim-tests.md` can run, then start it. Do every step you can yourself. Hand the user only the steps that need an administrator, a reboot, a password, or a login, and give each as one command or click, with what they will see. After each handoff, wait for the user to say they are done, then check that it worked before moving on.

## Ground rules

1. **Never see a password.** Do not ask for one in the chat, do not print `~/.netrc`, and never put credentials in the repo or in any log. The user types passwords only into a window or prompt you do not read.
2. **Ask before** anything that needs administrator rights, a reboot, `sudo`, Docker, `wsl --shutdown`, moving or resizing the WSL disk, or pushing to any server. Installing Miniforge into the Linux home folder and writing to `~/.bashrc` are fine without asking.
3. **Never run `wsl --shutdown` from inside WSL**; it would end this session. If a WSL setting change needs a restart of WSL, leave it for the end and tell the user.
4. Keep notes as you go (what you checked, what you installed, versions, anything the user did). S5 writes them to `prelim/SETUP.md` in the Linux copy of the repo.

## S1. Where am I?

Work out whether this session is running on Windows (PowerShell or Git Bash), inside WSL2, or on plain Linux. Inside WSL, `/proc/sys/fs/binfmt_misc/WSLInterop` exists and `uname -r` contains `microsoft`.

- **Windows:** do S2, then run every Linux step through `wsl.exe -d <distro> -- bash -lc '<command>'`. From Git Bash, set `MSYS_NO_PATHCONV=1` so Linux paths are not rewritten, and note that `wsl.exe` prints UTF-16 (strip the null bytes before reading its output).
- **Inside WSL2:** skip S2.
- **Plain Linux:** skip S2 and everything about Windows; the repo path in S3 will differ, so find it.

## S2. WSL2 and Ubuntu (Windows only)

- Run `wsl.exe --status` and `wsl.exe -l -v`. Use an existing Ubuntu distro on WSL version 2 if there is one; record its exact name.
- If WSL is missing, or Ubuntu is on version 1, stop and ask the user to open PowerShell **as administrator** and run `wsl --install -d Ubuntu` (or `wsl --set-version <distro> 2`), restart the PC when it asks, then open Ubuntu from the Start menu once and create the Linux username and password. When they say they are done, run `claude` again in this folder if the restart ended this session, and pick up here.
- Check free space on `C:` (the WSL disk lives there): at least 60 GB for the preliminary tests, and about 120 GB before 13 Nov for the full download list. If it is short, tell the user and stop; moving WSL to another drive is possible but needs their approval.

## S3. Linux side

All of this runs inside the Ubuntu distro.

- Check `free -g` and `nproc`. If WSL sees under 16 GB of RAM, note it; raising it means editing `%UserProfile%\.wslconfig` and restarting WSL, which you leave for the end and ask about.
- Check for `git`, `curl` and `unzip`. If any is missing, prefer getting it from conda-forge after the next step; only if that fails, ask the user to run `sudo apt-get install -y <packages>` in an Ubuntu window.
- Install Miniforge into `~/miniforge3` (user space, no `sudo`) if `conda` is not already on the path, and initialise it for bash.
- Make the data folders on the Linux disk: `~/dwts-data` and `~/dwts-out`. Add `export DWTS_DATA=$HOME/dwts-data` and `export DWTS_OUT=$HOME/dwts-out` to `~/.bashrc`. Confirm with `df -T ~` that home is ext4.
- Clone the repo onto the Linux disk: `git clone /mnt/c/Users/daria/PROJECT_DWTS ~/PROJECT_DWTS` (if `~/PROJECT_DWTS` already exists, `git pull` instead). The Windows folder becomes the clone's `origin`. Data and test outputs live on the Linux side, where large reads are many times faster than on `/mnt/c`.
- Set `git config user.name` and `user.email` in the clone if they are unset, copying them from the Windows repo's config.

## S4. Earthdata login

- Ask the user whether they have a NASA Earthdata account. If not, send them to [urs.earthdata.nasa.gov/users/new](https://urs.earthdata.nasa.gov/users/new) and wait until they have confirmed their email.
- Write this script to `~/dwts-setup/earthdata_netrc.sh` (outside the repo):

  ```bash
  #!/usr/bin/env bash
  set -e
  read -rp "Earthdata username: " u
  read -rsp "Earthdata password: " p; echo
  umask 077
  touch ~/.netrc
  grep -v "urs.earthdata.nasa.gov" ~/.netrc > ~/.netrc.tmp || true
  printf 'machine urs.earthdata.nasa.gov login %s password %s\n' "$u" "$p" >> ~/.netrc.tmp
  mv ~/.netrc.tmp ~/.netrc
  chmod 600 ~/.netrc
  echo "Saved. You can close this window."
  ```

- Open it in its own window so the user types into it, not into this chat. From Windows, or from inside WSL through interop: `cmd.exe /c start "Earthdata login" wsl.exe -d <distro> -- bash ~/dwts-setup/earthdata_netrc.sh`. If no window can be opened, ask the user to open an Ubuntu window and run `bash ~/dwts-setup/earthdata_netrc.sh` themselves.
- Check it worked without reading the file: `~/.netrc` exists with mode 600 and has a line for `urs.earthdata.nasa.gov` (test with `grep -c`, never print it). Then fetch the first 1 KB of two files from `data/manifest.csv` with `curl --netrc -L -c <cookie file> -b <cookie file> -r 0-1023 -o /dev/null -w '%{http_code}'`: one OPERA DSWx-HLS file and one NISAR GCOV file. Keep the cookie file in `~/dwts-setup/`.
  - 200 or 206 on both: done.
  - 401 on both: the username or password is wrong; run the window again.
  - The OPERA file works but NISAR is refused: ask the user to open that NISAR URL once in a browser while signed in to Earthdata and accept any data-use agreement it shows, then test again.

## S5. Start the tests

First write `prelim/SETUP.md` in `~/PROJECT_DWTS` with your notes: the distro and WSL version, RAM, cores and free disk, what you installed and where, what the user did by hand, and anything left for later (such as a `.wslconfig` change). Never include credentials. The tests commit it with their own files.

The tests must run in Linux, in `~/PROJECT_DWTS`.

- **If this session is inside WSL:** continue in this session. Work in `~/PROJECT_DWTS` (read its `CLAUDE.md` first), then read `prompts/prelim-tests.md` there and carry out everything below its line. Setup has already done T0's conda and Earthdata steps, so T0 only checks them.
- **If this session is on Windows:** check whether Claude Code is installed inside Ubuntu (`command -v claude`). If not, install it there with the official Linux method from the Claude Code documentation; do not guess the command. Then open the tests in a new window:

  ```
  cmd.exe /c start "DWTS prelim tests" wsl.exe -d <distro> -- bash -lc 'cd ~/PROJECT_DWTS && claude "Read prompts/prelim-tests.md and carry out everything below the line."'
  ```

  Tell the user a new window is opening, that it may ask them to log in to Claude once, and that the tests take several hours and write `prelim/REPORT.md` as they go.

## When you are done

Tell the user, in a few lines, what is set up, what they did by hand, and where the tests are running.
