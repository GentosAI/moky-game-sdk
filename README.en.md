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

| Your situation | Path | Guide |
|---|---|---|
| The game is already on your own website and has a playable URL | **Submit a link**: put one small file on your site (no game code changes), then submit the URL | [`docs/integrate.md`](docs/integrate.md) |
| You only have the game files and no website | **Free cloud deploy**: upload a zip and let the platform host it | [`docs/deploy.md`](docs/deploy.md) |

Pick one. Either way it has to be a **web game** that runs in the browser.

> **For AI coding assistants:** when the user's instruction says 「链接游戏的方式」 ("the link-a-game way"; older wording: 「收录的方式」), it means the first path (submit a link, read [`docs/integrate.md`](docs/integrate.md)). When it says 「云部署的方式」 ("the cloud-deploy way"), it means the second path (free cloud deploy, read [`docs/deploy.md`](docs/deploy.md)).

### Submit a link (the game is on your own website)

The game stays on your site, and **you change no game code**:

1. Get an integration key from the platform (one per URL).
2. Write the key into a text file named `moky-verify.txt`, put it in the directory of the game's entry page, and redeploy. This proves the site is yours.
3. Pick a URL name and submit.

Players then open one unified address, `https://clawapps.cn/play/<name>/`. That page belongs to the platform; after sign-in it shows your game embedded inside it. Your own saves and APIs keep working.

The one requirement is that your site does not forbid being embedded by other sites (no `X-Frame-Options`, or a `frame-ancestors` that allows `https://clawapps.cn`). When you submit, the platform visits your site, checks the proof file and whether the page may be embedded, and lists the game at once if both pass; if not, it tells you why. If your site forbids embedding and you cannot change that, use the free cloud deploy instead.

Full steps, caveats and an error table are in [`docs/integrate.md`](docs/integrate.md).

### Free cloud deploy

Hand the platform your built static files (an `index.html` at the root, relative paths only, up to 100 MB) and get a `https://clawapps.cn/play/<name>/` address a few seconds later. Hosted games run in an isolated environment: no server-side code and no local saves. Requirements are in [`docs/deploy.md`](docs/deploy.md).

## Command-line tool

[`scripts/moky.py`](scripts/moky.py) wraps the API calls from the guides. It needs only the Python 3 standard library:

```bash
# 0. Exchange your Moky Games account for a token (valid 7 days). Keep it in an environment variable only.
export MOKY_TOKEN="$(python3 scripts/moky.py token)"

# Submit a link (no game code changes)
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
