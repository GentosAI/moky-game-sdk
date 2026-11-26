# 蒙奇游戏开发者仓库（moky-game-sdk）

[English](README.en.md) | **中文**

蒙奇游戏是一个免费的 AI 游戏导航站：用 AI 做出来的网页游戏，可以免费上架到这里，被更多玩家看到。

- 官网：https://moky.com.cn
- 这个仓库是给开发者和他们的 **AI 编程助手**（Claude Code、Codex 等）读的：里面有完整的接入指引、现成的命令行工具、要嵌进游戏的代码，以及平台条款。

> **给 AI 编程助手：** 如果用户让你「把游戏发布 / 接入 / 部署到蒙奇游戏」，先读下面的「选哪条路」，再打开对应的指引逐步执行。指引里的每一步都有可以直接运行的命令。

## 平台怎么运作

1. 开发者用手机号在官网注册账号。
2. 把游戏上架到平台（两条路，见下）。上架是免费的。
3. 刚上架的游戏是**私有状态**：不在首页展示，开发者把链接或二维码发给朋友就能玩。玩家需要用蒙奇游戏账号登录后才能玩。
4. **有 20 位玩家玩过之后**（开发者自己不算），游戏自动出现在首页的「新品」里。
5. 开发者在官网右上角的「个人中心」查看游戏状态、玩家数，分享或删除游戏。

## 选哪条路

| 你的情况 | 走哪条路 | 指引 |
|---|---|---|
| 游戏已经放在你自己的网站上，有一个能直接玩的链接 | **提交链接收录**：在游戏页面里加一行登录脚本，然后提交链接 | [`docs/integrate.md`](docs/integrate.md) |
| 只有游戏文件，没有自己的网站 | **免费云部署**：把游戏打包上传，由平台托管 | [`docs/deploy.md`](docs/deploy.md) |

两条路二选一。不管哪条，游戏都必须是**网页游戏**（浏览器里打开就能玩）。

### 提交链接收录（外链游戏）

游戏留在你自己的网站上。你需要做两件事：

1. 在游戏入口页的 `<head>` 里加一行脚本（密钥向平台领取，每个链接一把）：

   ```html
   <script src="https://clawapps.cn/sdk/moky.js" data-game="你的接入密钥"></script>
   ```

2. 让游戏等登录完成再开始：

   ```js
   if (window.Moky) {
     Moky.onReady(function (player) {
       // player.id：这位玩家在你这款游戏里的固定匿名编号
       startGame(player);
     });
   }
   ```

提交时，平台会当场打开你的链接，检查页面里有没有带着你那把密钥的登录脚本。有，就说明链接确实是你的、登录也接好了，游戏立即收录。完整步骤、注意事项和出错对照见 [`docs/integrate.md`](docs/integrate.md)，可运行的例子见 [`examples/minimal-game/`](examples/minimal-game/)。

### 免费云部署

把构建好的静态文件（根目录要有 `index.html`，全部相对路径，100 MB 以内）交给平台，几秒钟后得到一个 `https://clawapps.cn/play/<网址名>/` 的地址。平台托管的游戏运行在隔离环境里，不支持服务端程序和本地存档。完整要求见 [`docs/deploy.md`](docs/deploy.md)。

## 命令行工具

[`scripts/moky.py`](scripts/moky.py) 把指引里的接口调用包成了命令，只依赖 Python 3 标准库：

```bash
# 0. 用蒙奇游戏账号换令牌（7 天有效）。令牌只放在环境变量里。
export MOKY_TOKEN="$(python3 scripts/moky.py token)"

# 提交链接收录
python3 scripts/moky.py key https://games.example.com/star-catch/        # 领取接入密钥和那一行脚本
#   ……把脚本加进游戏、按 docs/integrate.md 改好、重新发布到你的网站……
python3 scripts/moky.py check https://games.example.com/star-catch/ mk0123456789abcdef   # 自检
python3 scripts/moky.py submit --key mk0123456789abcdef --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 免费云部署
python3 scripts/moky.py deploy dist --name star-catch --title 接星星 \
    --intro '接住落下的星星，别碰到陨石。' --cat 休闲 --cover cover.png

# 查看我的游戏、状态和玩家数
python3 scripts/moky.py status
```

也可以不用这个工具，直接按指引里的 `curl` 命令调用接口，效果一样。

## 上架需要提供的信息

| 字段 | 要求 |
|---|---|
| 游戏名称 | 1–30 个字 |
| 一句话介绍 | 2–200 个字 |
| 分类 | 动作、射击、跑酷、治愈、休闲、策略、解谜、竞速 之一 |
| 封面图 | PNG / JPG / WebP，2 MB 以内；推荐竖版 900×1200 或横版 1280×720 |
| 游戏本身 | 外链：一个公网能打开的游戏链接；云部署：一个静态文件目录 |

## 仓库里有什么

| 路径 | 内容 |
|---|---|
| [`docs/integrate.md`](docs/integrate.md) | 外链游戏接入登录并提交收录的完整指引 |
| [`docs/deploy.md`](docs/deploy.md) | 免费云部署的完整指引 |
| [`scripts/moky.py`](scripts/moky.py) | 命令行工具 |
| [`examples/minimal-game/`](examples/minimal-game/) | 已接好登录的最小示例游戏 |
| [`sdk/moky.js`](sdk/moky.js) | 登录脚本的源码，供阅读。**接入时请引用线上地址 `https://clawapps.cn/sdk/moky.js`，不要拷贝这个文件**（平台只认线上地址） |
| [`legal/terms.md`](legal/terms.md) | 用户协议 |
| [`legal/privacy.md`](legal/privacy.md) | 隐私政策 |

指引的线上版本（和仓库保持一致）：https://clawapps.cn/integrate.md 、https://clawapps.cn/deploy.md

## 安全须知

- **令牌和密码不要写进任何文件，不要提交到代码仓库。** 令牌只放在环境变量 `MOKY_TOKEN` 里。
- 接入密钥（`mk…`）不是秘密，它本来就写在你的游戏页面里。
- 登录脚本只告诉游戏一个匿名的玩家编号，不会把玩家的手机号交给游戏。
- 让 AI 助手代你操作时，推荐你自己运行 `python3 scripts/moky.py token`，只把令牌交给它，不要把密码告诉它。

## 规则和条款

上架即表示同意 [用户协议](legal/terms.md) 和 [隐私政策](legal/privacy.md)。要点：

- 你要对自己的游戏拥有合法权利，内容不得违法、侵权或泄露他人隐私。
- 游戏违法违规、被投诉且有初步证据、存在安全风险，或登录脚本被去掉、被绕过时，平台有权下架。
- 平台目前免费提供，不保证服务不中断。

## 联系我们

合作、投诉、账号问题：hi@moky.ai ，或在官网页脚点「联系蒙奇工作室」。
