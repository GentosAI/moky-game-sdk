# Moky Games developer repo (moky-game-sdk)

**English** | [中文](README.md)

Moky Games (蒙奇游戏) is a free directory of AI-made browser games. If you built a web game with AI, you can list it here for free and get it in front of more players.

- Website: https://moky.com.cn (Chinese)
- This repository is written for developers and their **AI coding assistants** (Claude Code, Codex, and others). It holds the full integration guides, a ready-to-run command-line tool, and the platform terms.

> **For AI coding assistants:** if the user asks you to "publish / integrate / deploy the game to Moky Games", read "Which path to take" below, then open the matching guide and follow it step by step. Every step has a command you can run as written. The guides are in Chinese; the commands and JSON fields are the same in any language.

Accounts need a mainland China mobile number, and the website and guides are in Chinese for now.

## How the platform works

1. The developer signs up on the website with a mobile number.
2. The game is listed on the platform (two paths, see below). Listing is free.
3. A newly listed game is **private**: it is not shown on the home page, and the developer shares the link or QR code with friends. Players sign in with a Moky Games account before they can play.
4. **After 20 players have played it** (the developer does not count), the game appears automatically under "New" (新品) on the home page.
5. The developer opens "个人中心" (My account) at the top right of the website to see status and player count, and to share or remove games.

## Which path to take

| Wording in the user's instruction | When it fits | What you do | Full guide |
|---|---|---|---|
| 「链接游戏的方式」 ("the link-a-game way"; older wording: 「收录的方式」) | The game is already on your own website and has a playable URL | **Link a game**: put one small file on your site (no game code changes), then submit the URL | [`docs/integrate.md`](docs/integrate.md) |
| 「云部署的方式」 ("the cloud-deploy way") | You only have the game files and no website | **Free cloud deploy**: upload a zip and let the platform host it | [`docs/deploy.md`](docs/deploy.md) |

Pick one. Either way it has to be a **web game** that runs in the browser, and the listed address is `https://clawapps.cn/play/<name>/`.

> **For AI coding assistants:**
> - Take the path the user named. If they did not say: the game already has a public URL and the user can put files on that site → link a game; otherwise → free cloud deploy.
> - The two sections below are the complete flow for each path. Before you start, also open the matching full guide: it has response examples for every call, all limits and the error table.
> - Full guides (same content, use whichever opens):
>   - Link a game: https://github.com/GentosAI/moky-game-sdk/blob/main/docs/integrate.md | https://clawapps.cn/integrate.md
>   - Free cloud deploy: https://github.com/GentosAI/moky-game-sdk/blob/main/docs/deploy.md | https://clawapps.cn/deploy.md
> - If the user is not around to answer: choose the title, description, category and URL name yourself within the rules, finish the job, then tell the user what you used.

## Before either path

**1. Account.** The user needs a Moky Games account (sign up with a mobile number and set a password at the top right of https://moky.com.cn). If they have none, ask them to sign up first.

**2. Token.** Exchange the mobile number and password for a token. It is valid for 7 days and every later step sends it:

```bash
curl -sS -X POST 'https://clawapps.cn/api/auth/token' \
  -H 'Content-Type: application/json' \
  -d '{"phone":"USER_MOBILE_NUMBER","password":"USER_PASSWORD"}'
# success: {"ok":true,"token":"clt_…","expires_in":604800}
export MOKY_TOKEN='clt_…'
```

Prefer that the user runs this command (or `python3 scripts/moky.py token`) and hands you only the token. Never write the password or the token to a file, commit them, or print them to logs.

**3. Game details and cover.** Both paths need the same details, see "What you provide when listing" below. Use a real screenshot of the game as the cover.

**4. Tool (optional).** [`scripts/moky.py`](scripts/moky.py) wraps the API calls as commands and needs only the Python 3 standard library. Clone this repository (`git clone https://github.com/GentosAI/moky-game-sdk.git`) to use it; if you would rather not, every step in the full guides has an equivalent `curl` command.

## Path 1: link a game (the game is on your own website)

The game stays on your site, and **you change no game code**. Once listed, players open the platform page `https://clawapps.cn/play/<name>/`, and after sign-in your game runs embedded in it. Your own saves and APIs keep working, and when you update your site the listed game updates with it.

**Requirements**

- The game URL starts with `http://` or `https://` and uses a domain name (no IP address or localhost, default ports 80 / 443 only), and opens on the public internet without sign-in.
- It is your own site: you can add a file to the game directory and redeploy.
- The site does not forbid being embedded: no `X-Frame-Options` header, or the `frame-ancestors` directive of `Content-Security-Policy` allows `https://clawapps.cn`. If embedding is forbidden and you cannot change that, use free cloud deploy instead.

**Steps**

```bash
# 1. Get an integration key (one per game URL; use this same URL in every later step)
python3 scripts/moky.py key https://games.example.com/star-catch/

# 2. Write the key into moky-verify.txt, put it next to the game's entry page, then redeploy your site your usual way
#    Afterwards https://games.example.com/star-catch/moky-verify.txt must open and contain the key
echo 'mk0123456789abcdef' > moky-verify.txt

# 3. Self-check: is the proof file there, does the site allow embedding
python3 scripts/moky.py check https://games.example.com/star-catch/ mk0123456789abcdef

# 4. Submit (--name is the URL name: starts with a lowercase letter, 3–31 characters, lowercase letters, digits and hyphens only)
python3 scripts/moky.py submit --key mk0123456789abcdef --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 5. Confirm: the game's status in the list should be live
python3 scripts/moky.py status
```

On submit the platform visits your site right away and checks the proof file and whether the page can be embedded. If both pass the game is listed immediately; if not, the response names the reason (see section 7 of [`docs/integrate.md`](docs/integrate.md)).

**Tell the user when done**

- The address `https://clawapps.cn/play/<name>/`, and the title, description, category and URL name you used.
- `moky-verify.txt` has to stay on the site; if it is removed the platform may take the game down on a re-check.
- To change the title, description, category or cover later: submit again with the same key and the same URL name.

## Path 2: free cloud deploy (the platform hosts the game files)

Hand the built static files to the platform and get `https://clawapps.cn/play/<name>/`, usually within seconds. No website or server of your own is needed.

**Requirements**

- A purely static single-player web game: `index.html` at the root of the build output; no server-side code.
- Relative paths only (`./js/main.js`, `assets/a.png`); paths starting with `/` will not load. With Vite, set `base` to `'./'`.
- The game runs in an isolated environment: `localStorage`, `sessionStorage`, cookies and `IndexedDB` are unavailable (access throws, so wrap it in `try / catch` and keep saves in memory); `window.open` and new-window links do not work; do not rely on external APIs, CDNs, hosted fonts or analytics scripts, bundle every dependency.
- Size: zip up to 100 MB; unpacked up to 400 MB and 5000 files.

**Steps**

```bash
# 1. Build first if the project needs it; you deploy the build output (usually dist/)
npm run build

# 2. Local check: open it under a sub-path, confirm it plays, the console is clean and nothing is requested from other domains
mkdir -p /tmp/moky-check/play && ln -sfn "$PWD/dist" /tmp/moky-check/play/my-game
(cd /tmp/moky-check && python3 -m http.server 8765)   # open http://127.0.0.1:8765/play/my-game/

# 3. Deploy: this zips the directory, uploads the cover and the package, and waits until the deploy finishes
python3 scripts/moky.py deploy dist --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 4. Confirm: the game's status in the list should be live, and url is the game address
python3 scripts/moky.py status
```

Without the tool, step 3 is three calls: upload the cover `POST /api/games/cover` → upload the package `POST /api/games/upload` → poll `GET /api/games/mine` every 2–3 seconds until `status` is no longer `queued`. Full commands and the error table are in sections 4–8 of [`docs/deploy.md`](docs/deploy.md). The game address needs sign-in, so requesting it without one returns HTTP 302; that is expected.

**Tell the user when done**

- The address `https://clawapps.cn/play/<name>/`, and the title, description, category and URL name you used; also say honestly whether you actually played it in a browser.
- To update the game later: deploy again with the same URL name.

## How the two paths differ

| | Link a game | Free cloud deploy |
|---|---|---|
| Where the game files live | Your own website | The platform |
| Game code changes | None | Usually none; needed if the game uses local storage or absolute paths |
| Local saves, your own server APIs | Work as usual | Not available (isolated, static only) |
| Multiplayer / games that need a back end | Yes | Not supported |
| Updating the game | Update your own site | Deploy again with the same URL name |
| Listed address | `https://clawapps.cn/play/<name>/` | `https://clawapps.cn/play/<name>/` |

Rules shared by both paths:

- Up to 5 games per account (both paths combined). List a game through one path only, not both.
- A new listing is private and players sign in to play; after 20 players have played it (the developer does not count) it appears automatically under "New" (新品) on the home page.
- Status, player count, share QR code and removal: "个人中心" (My account) at the top right of the website. Linked games are under 「链接的游戏」, cloud-deployed games under 「云部署的游戏」.
- Removing by command: `python3 scripts/moky.py remove <name> --yes`. Removal makes the game address stop working at once, so get the user's explicit consent first.

## Command-line tool

[`scripts/moky.py`](scripts/moky.py) wraps the API calls from the guides. It needs only the Python 3 standard library:

```bash
# 0. Exchange your Moky Games account for a token (valid 7 days). Keep it in an environment variable only.
export MOKY_TOKEN="$(python3 scripts/moky.py token)"

# Link a game (no game code changes)
python3 scripts/moky.py key https://games.example.com/star-catch/        # get the integration key
echo 'mk0123456789abcdef' > moky-verify.txt                              # put it in the game directory, redeploy your site
python3 scripts/moky.py check https://games.example.com/star-catch/ mk0123456789abcdef   # self-check
python3 scripts/moky.py submit --key mk0123456789abcdef --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# Free cloud deploy
python3 scripts/moky.py deploy dist --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# List my games, their status and player counts
python3 scripts/moky.py status
```

You can also skip the tool and call the API with the `curl` commands in the guides.

## What you provide when listing

| Field | Rule |
|---|---|
| Title | 1 to 30 characters |
| One-line description | 2 to 200 characters |
| Category | exactly one of: 动作 (action), 射击 (shooter), 跑酷 (runner), 治愈 (cozy), 休闲 (casual), 策略 (strategy), 解谜 (puzzle), 竞速 (racing). Send the Chinese value |
| Cover image | PNG / JPG / WebP, up to 2 MB; 900×1200 portrait or 1280×720 landscape recommended |
| The game | link path: a publicly reachable game URL; cloud deploy: a directory of static files |

## What is in this repository

| Path | Contents |
|---|---|
| [`docs/integrate.md`](docs/integrate.md) | Full guide: submit the URL of a self-hosted game (Chinese) |
| [`docs/deploy.md`](docs/deploy.md) | Full guide: free cloud deploy (Chinese) |
| [`scripts/moky.py`](scripts/moky.py) | Command-line tool |
| [`legal/terms.md`](legal/terms.md) | Terms of service (Chinese) |
| [`legal/privacy.md`](legal/privacy.md) | Privacy policy (Chinese) |

Hosted copies of the guides (kept in sync with this repo): https://clawapps.cn/integrate.md and https://clawapps.cn/deploy.md

## Security notes

- **Never write the token or password to a file, and never commit them.** Keep the token in the `MOKY_TOKEN` environment variable.
- The integration key (`mk…`) is not a secret; it sits in the proof file on your site.
- The platform never passes a player's phone number or any account data to the game.
- When an AI assistant acts for you, run `python3 scripts/moky.py token` yourself and hand it the token rather than your password.

## Rules and terms

Listing a game means you accept the [terms of service](legal/terms.md) and the [privacy policy](legal/privacy.md). In short:

- You must hold the rights to your game, and its content must not be illegal, infringing, or leak other people's private data.
- The platform may take a game down if it breaks the law or the terms, if it receives a complaint with initial evidence, if there is a security risk, or if the proof file is removed.
- The service is free for now and comes with no uptime guarantee.

## Contact

Partnerships, complaints, account issues: hi@moky.ai
