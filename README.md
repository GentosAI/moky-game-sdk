# 蒙奇大陆开发者仓库（moky-game-sdk）

[English](README.en.md) | **中文**

蒙奇大陆是一个免费的 AI 游戏导航站：用 AI 做出来的网页游戏，可以免费上架到这里，被更多玩家看到。

- 官网：https://moky.com.cn
- 这个仓库是给开发者和他们的 **AI 编程助手**（Claude Code、Codex 等）读的：里面有完整的接入指引、现成的命令行工具，以及平台条款。

> **给 AI 编程助手：** 如果用户让你「把游戏发布 / 接入 / 部署到蒙奇大陆」，先读下面的「选哪条路」，再打开对应的指引逐步执行。指引里的每一步都有可以直接运行的命令。

## 平台怎么运作

1. 开发者用手机号在官网注册账号。
2. 把游戏上架到平台（两条路，见下）。上架是免费的。
3. 刚上架的游戏是**私有状态**：不在首页展示，开发者把链接或二维码发给朋友就能玩。玩家需要用蒙奇大陆账号登录后才能玩。
4. **有 20 位玩家玩过之后**（开发者自己不算），游戏自动出现在首页的「新品」里。
5. 开发者在官网右上角的「创作中心」查看游戏状态、玩家数，分享或删除游戏。

## 选哪条路

| 用户指令里的说法 | 适合的情况 | 做法 | 完整指引 |
|---|---|---|---|
| 「链接游戏的方式」（旧说法：「收录的方式」） | 游戏已经放在你自己的网站上，有一个能直接玩的链接 | **链接游戏**：在网站上放一个小文件（不改游戏代码），然后提交链接 | [`docs/integrate.md`](docs/integrate.md) |
| 「云部署的方式」 | 只有游戏文件，没有自己的网站 | **免费云部署**：把游戏打包上传，由平台托管 | [`docs/deploy.md`](docs/deploy.md) |

两条路二选一。不管哪条，游戏都必须是**网页游戏**（浏览器里打开就能玩），上架后的地址都是 `https://clawapps.cn/play/<网址名>/`。

> **给 AI 编程助手：**
> - 用户说了哪种方式就走哪条路。没说清时这样判断：游戏已经有公网能打开的地址、并且用户能往那个网站上放文件 → 链接游戏；否则 → 免费云部署。
> - 下面两节是每条路的完整流程，照着做就能完成。做之前请再打开对应的完整指引：里面有每个接口的返回示例、全部限制和出错对照表。
> - 完整指引的地址（内容相同，任选一个能打开的）：
>   - 链接游戏：https://github.com/GentosAI/moky-game-sdk/blob/main/docs/integrate.md ｜ https://clawapps.cn/integrate.md
>   - 免费云部署：https://github.com/GentosAI/moky-game-sdk/blob/main/docs/deploy.md ｜ https://clawapps.cn/deploy.md
> - 用户不在场、没法回答问题时：游戏名称、介绍、分类、网址名按要求自己拟定，直接做完，完成后把用到的信息一并告诉用户。

## 两条路都要先做的事

**1. 账号。** 用户要有蒙奇大陆账号（在 https://moky.com.cn 右上角用手机号注册并设置密码）。没有的话请用户先注册。

**2. 令牌。** 用手机号和密码换一个令牌，7 天有效，之后每一步都带它：

```bash
curl -sS -X POST 'https://clawapps.cn/api/auth/token' \
  -H 'Content-Type: application/json' \
  -d '{"phone":"用户的手机号","password":"用户的密码"}'
# 成功返回 {"ok":true,"token":"clt_…","expires_in":604800}
export MOKY_TOKEN='clt_…'
```

推荐请用户自己运行这条命令（或 `python3 scripts/moky.py token`），只把令牌交给你。密码和令牌不要写进任何文件、不要提交到代码仓库、不要打印到日志里。

**3. 游戏信息和封面。** 两条路要的信息一样，见下面的「上架需要提供的信息」。封面用游戏的真实画面。

**4. 工具（可选）。** [`scripts/moky.py`](scripts/moky.py) 把接口包成了命令，只依赖 Python 3 标准库。克隆本仓库（`git clone https://github.com/GentosAI/moky-game-sdk.git`）即可使用；不想用它，完整指引里每一步都有等价的 `curl` 命令。

## 方式一：链接游戏（游戏在你自己的网站上）

游戏留在你自己的网站上，**游戏代码一行都不用改**。收录后，玩家打开的是平台的页面 `https://clawapps.cn/play/<网址名>/`，登录后你的游戏嵌在里面运行；你自己的存档和接口照常可用，你更新自己的网站，平台上的游戏随之更新。

**前提**

- 游戏链接是 `http://` 或 `https://` 开头的域名地址（不能是 IP 或 localhost，端口只能是默认的 80 / 443），公网上不登录就能打开。
- 是你自己的网站：能往游戏目录里放一个文件并重新发布。
- 网站没有禁止被别的网站嵌入：没有 `X-Frame-Options` 响应头，或 `Content-Security-Policy` 的 `frame-ancestors` 放行了 `https://clawapps.cn`。禁止嵌入又改不了的，请改用免费云部署。

**步骤**

```bash
# 1. 领取接入密钥（每个游戏链接一把；之后每一步用的都是这同一个链接）
python3 scripts/moky.py key https://games.example.com/star-catch/

# 2. 把密钥写进 moky-verify.txt，放到游戏入口页所在的目录，然后按你自己的方式重新发布网站
#    发布后 https://games.example.com/star-catch/moky-verify.txt 应当能打开，内容就是密钥
echo 'mk0123456789abcdef' > moky-verify.txt

# 3. 自检：归属文件在不在、网站是否允许被嵌入
python3 scripts/moky.py check https://games.example.com/star-catch/ mk0123456789abcdef

# 4. 提交（--name 是网址名：小写字母开头，3–31 位，只含小写字母、数字、连字符）
python3 scripts/moky.py submit --key mk0123456789abcdef --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 5. 确认：列表里这款游戏的 status 应当是 live
python3 scripts/moky.py status
```

提交时平台会当场访问你的网站，检查归属文件和能否嵌入：通过就立即收录，不通过会返回明确的原因（对照 [`docs/integrate.md`](docs/integrate.md) 第 7 节处理）。

**完成后告诉用户**

- 游戏地址 `https://clawapps.cn/play/<网址名>/`，以及这次用的名称、介绍、分类、网址名。
- `moky-verify.txt` 要一直留在网站上，去掉后平台复查时可以把游戏下架。
- 以后要改名称、介绍、分类或封面：用同一把密钥和同一个网址名再提交一次。

## 方式二：免费云部署（把游戏文件交给平台托管）

把构建好的静态文件交给平台，通常几秒钟后得到 `https://clawapps.cn/play/<网址名>/`。不需要自己的网站和服务器。

**前提**

- 纯静态的单机网页游戏：产物根目录有 `index.html`；不支持服务端程序。
- 全部使用相对路径（`./js/main.js`、`assets/a.png`），以 `/` 开头的路径会加载不到。用 Vite 构建的把 `base` 设成 `'./'`。
- 游戏运行在隔离环境里：`localStorage`、`sessionStorage`、`cookie`、`IndexedDB` 不可用（访问会抛错，要包上 `try / catch`，存档只能留在内存里）；`window.open` 和新窗口链接不可用；不要依赖外部接口、CDN、外链字体或统计脚本，所有依赖都打进包里。
- 大小：zip 不超过 100 MB；解开后不超过 400 MB、5000 个文件。

**步骤**

```bash
# 1. 项目需要构建的先构建，部署的是构建产物目录（通常是 dist/）
npm run build

# 2. 本地自检：放在子路径下打开，确认能玩、控制台没有报错、没有请求发往别的域名
mkdir -p /tmp/moky-check/play && ln -sfn "$PWD/dist" /tmp/moky-check/play/my-game
(cd /tmp/moky-check && python3 -m http.server 8765)   # 访问 http://127.0.0.1:8765/play/my-game/

# 3. 部署：这条命令会打包、上传封面和游戏包，并等到部署完成
python3 scripts/moky.py deploy dist --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 4. 确认：列表里这款游戏的 status 应当是 live，url 就是游戏地址
python3 scripts/moky.py status
```

不用工具时，第 3 步对应三个接口：上传封面 `POST /api/games/cover` → 上传游戏包 `POST /api/games/upload` → 每 2–3 秒查一次 `GET /api/games/mine` 直到 `status` 不再是 `queued`。完整命令和出错对照见 [`docs/deploy.md`](docs/deploy.md) 第 4–8 节。游戏地址需要登录才能打开，不登录直接请求会得到 HTTP 302，这是正常的。

**完成后告诉用户**

- 游戏地址 `https://clawapps.cn/play/<网址名>/`，以及这次用的名称、介绍、分类、网址名；有没有在浏览器里实际玩过也要如实说明。
- 以后更新游戏：用同一个网址名再部署一次。

## 两种方式的区别

| | 链接游戏 | 免费云部署 |
|---|---|---|
| 游戏文件放在哪 | 你自己的网站 | 平台 |
| 要不要改游戏代码 | 不用 | 一般不用；用了本地存储或绝对路径的要改 |
| 本地存档、自己的服务端接口 | 照常可用 | 不可用（隔离环境，纯静态） |
| 联机 / 需要后端的游戏 | 可以 | 不支持 |
| 更新游戏 | 更新你自己的网站即可 | 用同一个网址名再部署一次 |
| 上架后的地址 | `https://clawapps.cn/play/<网址名>/` | `https://clawapps.cn/play/<网址名>/` |

两种方式共同的规则：

- 每个账号最多 5 款游戏（两种方式合计）。同一款游戏只走一条路，不要重复上架。
- 刚上架是私有状态，玩家登录后才能玩；有 20 位玩家玩过之后（开发者自己不算）自动出现在首页「新品」。
- 查看状态、玩家数、分享二维码、删除游戏：官网右上角「创作中心」。链接的游戏在「链接的游戏」里，云部署的游戏在「云部署的游戏」里。
- 用命令删除：`python3 scripts/moky.py remove <网址名> --yes`。删除会让游戏地址立刻失效，执行前必须得到用户明确同意。

## 命令行工具

[`scripts/moky.py`](scripts/moky.py) 把指引里的接口调用包成了命令，只依赖 Python 3 标准库：

```bash
# 0. 用蒙奇大陆账号换令牌（7 天有效）。令牌只放在环境变量里。
export MOKY_TOKEN="$(python3 scripts/moky.py token)"

# 链接游戏（不改游戏代码）
python3 scripts/moky.py key https://games.example.com/star-catch/        # 领取接入密钥
echo 'mk0123456789abcdef' > moky-verify.txt                              # 放到游戏目录，重新发布你的网站
python3 scripts/moky.py check https://games.example.com/star-catch/ mk0123456789abcdef   # 自检
python3 scripts/moky.py submit --key mk0123456789abcdef --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 免费云部署
python3 scripts/moky.py deploy dist --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 查看我的游戏、状态和玩家数
python3 scripts/moky.py status
```

两条路的完整流程见上面两节。也可以不用这个工具，直接按指引里的 `curl` 命令调用接口，效果一样。

## 上架需要提供的信息

| 字段 | 要求 |
|---|---|
| 游戏名称 | 1–30 个字 |
| 一句话介绍 | 2–200 个字 |
| 分类 | 动作、射击、跑酷、治愈、休闲、策略、解谜、竞速 之一 |
| 封面图 | PNG / JPG / WebP，2 MB 以内；推荐竖版 900×1200 或横版 1280×720 |
| 游戏本身 | 链接游戏：一个公网能打开的游戏链接；云部署：一个静态文件目录 |

## 仓库里有什么

| 路径 | 内容 |
|---|---|
| [`docs/integrate.md`](docs/integrate.md) | 链接游戏（提交游戏链接收录）的完整指引 |
| [`docs/deploy.md`](docs/deploy.md) | 免费云部署的完整指引 |
| [`scripts/moky.py`](scripts/moky.py) | 命令行工具 |
| [`legal/terms.md`](legal/terms.md) | 用户协议 |
| [`legal/privacy.md`](legal/privacy.md) | 隐私政策 |

指引的线上版本（和仓库保持一致）：https://clawapps.cn/integrate.md 、https://clawapps.cn/deploy.md

## 安全须知

- **令牌和密码不要写进任何文件，不要提交到代码仓库。** 令牌只放在环境变量 `MOKY_TOKEN` 里。
- 接入密钥（`mk…`）不是秘密，它本来就放在你网站上的归属文件里。
- 平台不会把玩家的手机号或任何账号信息交给游戏。
- 让 AI 助手代你操作时，推荐你自己运行 `python3 scripts/moky.py token`，只把令牌交给它，不要把密码告诉它。

## 规则和条款

上架即表示同意 [用户协议](legal/terms.md) 和 [隐私政策](legal/privacy.md)。要点：

- 你要对自己的游戏拥有合法权利，内容不得违法、侵权或泄露他人隐私。
- 游戏违法违规、被投诉且有初步证据、存在安全风险，或归属文件被去掉时，平台有权下架。
- 平台目前免费提供，不保证服务不中断。

## 联系我们

合作、投诉、账号问题：hi@moky.ai ，或在官网页脚点「联系蒙奇工作室」。
