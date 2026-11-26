# 蒙奇游戏 · 提交游戏链接收录指引（给 AI 编程助手）

你正在帮用户把一款**已经放在他自己网站上的网页游戏**收录到蒙奇游戏（clawapps.cn）。收录后：

- 游戏得到一个统一的地址 `https://clawapps.cn/play/<网址名>/`（方式 A），或者继续用它自己的地址（方式 B）；
- 玩家用蒙奇游戏账号登录后才能玩，平台由此统计有多少位玩家玩过；
- 游戏先是私有状态，有 20 位玩家玩过之后，出现在蒙奇游戏首页的「新品」里。

如果用户没有自己的网站、只是想把游戏文件交给平台托管，请改看另一份文档：https://clawapps.cn/deploy.md 。几条路选一条即可：同一款游戏做多次，平台上会出现多条互不相干的记录，玩家数分开算。

## 两种方式，先选一种

| | 方式 A：嵌入（默认，不改游戏代码） | 方式 B：接入登录脚本 |
|---|---|---|
| 你要做的 | 在游戏网站上放一个小文本文件 | 在游戏页面里加一行脚本，并让游戏等登录完成再开始 |
| 玩家打开的地址 | `https://clawapps.cn/play/<网址名>/`，平台的页面把游戏嵌在里面 | 游戏自己的地址 |
| 登录在哪拦 | 平台的页面上 | 游戏页面里的登录遮罩 |
| 游戏能拿到玩家编号吗 | 不能 | 能（`player.id`，可做排行榜等） |
| 什么时候不能用 | 游戏网站禁止被别的网站嵌入时（见 3A.2） | 都能用 |

**默认用方式 A。** 只有在方式 A 的检查通不过，或者用户明确想在游戏里用玩家编号时，才用方式 B。

请按顺序执行，每一步完成后再做下一步。

通用约定：

- 所有接口返回 JSON，请用 JSON 解析后判断，不要做字符串匹配。
- 成功时 HTTP 状态是 200 且带 `"ok":true`；失败时 HTTP 状态是 4xx / 5xx，返回 `{"error":"错误码"}`，有的还带 `"reason"`，意思见第 7 节。
- 如果用户不在场、没法回答问题：游戏信息按要求自己拟定，直接做完，完成后把你用的信息一并告诉用户。

## 0. 获取令牌

接入需要用户的蒙奇游戏账号（在 https://moky.com.cn 右上角用手机号注册）。用手机号和密码换一个令牌，之后的每一步都带这个令牌，7 天内有效：

```bash
curl -sS -X POST 'https://clawapps.cn/api/auth/token' \
  -H 'Content-Type: application/json' \
  -d '{"phone":"用户的手机号","password":"用户的密码"}'
```

成功返回 `{"ok":true,"token":"clt_…","expires_in":604800}`。把 `token` 放进环境变量：

```bash
export MOKY_TOKEN='clt_…'
```

- 手机号和密码请向用户要，或者请用户自己运行上面这条命令、只把返回的令牌给你（推荐：用户在你运行命令的同一个终端里先执行 `export MOKY_TOKEN=…`；如果用户给的是一个存着令牌的文件，只把它读进环境变量，不要复制、不要改动）。
- 密码和令牌都不要写进任何文件、不要提交到代码仓库、不要打印到日志里。
- 返回 `bad_login`：手机号或密码不对，或者这个号还没注册。返回 `too_many`：尝试太多次，等 15 分钟再试。

## 1. 确认游戏链接

先和用户确认（或从项目里找出）游戏上线后的**访问地址**，也就是玩家在浏览器里打开就能玩的那个页面的完整网址，例如 `https://games.example.com/star-catch/`。要求：

| 项 | 要求 |
|---|---|
| 协议和域名 | `http://` 或 `https://` 开头，必须是域名，不能是 IP 地址或 localhost |
| 端口 | 只能是默认的 80 / 443 |
| 可访问 | 公网上不登录就能打开，直接返回游戏的 HTML 页面（HTTP 200；允许最多 3 次跳转） |
| 归属 | 是用户自己的网站：他能往上面放文件、能重新发布 |

之后每一步用的都必须是这同一个地址。

## 2. 领取接入密钥

```bash
curl -sS -X POST 'https://clawapps.cn/api/sites/key' \
  -H "Authorization: Bearer $MOKY_TOKEN" -H 'Content-Type: application/json' \
  -d '{"url":"https://games.example.com/star-catch/"}'
```

成功返回：

```json
{"ok":true,"key":"mk0123456789abcdef","url":"https://games.example.com/star-catch/",
 "snippet":"<script src=\"https://clawapps.cn/sdk/moky.js\" data-game=\"mk0123456789abcdef\"></script>"}
```

- `key` 是这个账号、这个链接专用的接入密钥，同一个链接再领一次还是同一把。密钥不是秘密。
- `url` 是平台整理后的地址，后面以它为准。
- `snippet` 只有方式 B 用得到。

## 3A. 方式 A：嵌入（不改游戏代码）

### 3A.1 放一个归属文件

在游戏入口页**所在的目录**下放一个名为 `moky-verify.txt` 的文本文件，内容就是第 2 节领到的密钥（一行）：

```bash
echo 'mk0123456789abcdef' > moky-verify.txt   # 放在和游戏的 index.html 同一个目录
```

然后按用户项目自己的方式重新发布，让它能通过网址访问。文件的地址是「游戏地址所在目录 + `moky-verify.txt`」，例如游戏地址是 `https://games.example.com/star-catch/`，文件就是 `https://games.example.com/star-catch/moky-verify.txt`；游戏地址是 `https://games.example.com/play.html`，文件就是 `https://games.example.com/moky-verify.txt`。

这个文件用来证明网站是用户自己的。它不影响游戏，上架后也请一直留着。用构建工具的项目，把它放进会原样拷贝到产物里的目录（例如 Vite 的 `public/`）。

### 3A.2 自检

```bash
# 归属文件能访问，内容是密钥
curl -sSL 'https://games.example.com/star-catch/moky-verify.txt'

# 游戏页面没有禁止被嵌入
curl -sSIL 'https://games.example.com/star-catch/' | grep -iE '^(x-frame-options|content-security-policy):'
```

第二条命令**没有输出最好**。如果输出里有 `X-Frame-Options: DENY` / `SAMEORIGIN`，或者 `Content-Security-Policy` 里有 `frame-ancestors` 且没有放行 `https://clawapps.cn`，说明网站禁止被嵌入，方式 A 会被拒绝（`not_embeddable`）。这时二选一：

- 用户能改网站的响应头：去掉 `X-Frame-Options`，或者把 `frame-ancestors` 改成包含 `https://clawapps.cn`，然后继续方式 A；
- 改不了：换用方式 B（跳到 3B）。

游戏在嵌入环境里运行时：自己的本地存档、自己域名下的接口都照常可用；不能把整个浏览器页面跳转到别处（`top.location`）；全屏、手柄、陀螺仪可以用。

### 3A.3 选一个网址名

网址名 `name`：小写字母开头，3–31 位，只含小写字母、数字、连字符。游戏的统一地址就是 `https://clawapps.cn/play/<name>/`。用户没指定时，用项目名或游戏英文名拟一个。

做完 3A 直接跳到第 4 节。

## 3B. 方式 B：接入登录脚本

### 3.1 加一行脚本

把 `snippet` 原样放进游戏入口页（第 1 节那个地址返回的 HTML）的 `<head>` 里，或者放在游戏自己的脚本**之前**：

```html
<script src="https://clawapps.cn/sdk/moky.js" data-game="mk0123456789abcdef"></script>
```

必须满足，否则第 5 节的提交检查通不过：

- 这一行要**直接写在入口页的 HTML 源码里**。平台检查时只读 HTML 源码，不执行脚本，所以用 JS 动态插入的不算。用构建工具的，把它写进 `index.html` 模板。
- `src` 必须是 `https://clawapps.cn/sdk/moky.js`，不要下载到本地、不要改名、不要打包进自己的脚本。
- `data-game` 必须是第 2 节领到的那把密钥。
- 不要加 `type="module"`。可以不加 `async` / `defer`。

### 3.2 等登录完成再开始游戏

脚本加载后提供一个全局对象 `Moky`。玩家没登录时，脚本会自动盖一层「登录后开始玩」的遮罩，玩家点「登录蒙奇游戏」去登录，登录后自动回到游戏页，遮罩消失。

你要做的是：**让游戏在 `Moky.onReady` 之后才能开始**。两种常见情况：

- 页面一加载就开始的游戏：把原来的启动调用挪进 `Moky.onReady`。
- 有「开始」按钮的游戏：按钮先禁用，在 `Moky.onReady` 里再启用。

```js
// 原来：startGame();
Moky.onReady(function (player) {
  // player.id：这位玩家在你这款游戏里的固定编号（20 位字符，匿名，不是手机号）。
  // 同一个人每次来都是同一个 id，可以用来区分玩家、存排行榜等。
  startGame(player);
});
```

如果登录脚本没加载成功（被网络拦截、超时），`Moky` 不存在，直接调用会报错。请先判断，并给玩家一句提示，不要让页面静悄悄地卡住：

```js
if (window.Moky) {
  Moky.onReady(function (player) { startGame(player); });
} else {
  showMessage('登录组件没有加载成功，请刷新页面重试。');   // 用你游戏里现成的提示方式
}
```

说明：

- 加载顺序：按 3.1 把脚本放在 `<head>` 里（不加 `async` / `defer`），它会在页面其他脚本之前执行完，所以后面的脚本——包括带 `defer`、`async` 或 `type="module"` 的——运行时 `Moky` 都已经可用。
- `Moky.onReady(fn)`：登录完成后调用 `fn(player)`；如果已经登录过，立刻调用。可以注册多次。
- `Moky.ready`（布尔）、`Moky.player`（`{id}` 或 `null`）：随时读当前状态。
- 也可以监听事件：`window.addEventListener('moky:ready', function (e) { e.detail.id })`。
- 登录一次后在这个浏览器标签页里 12 小时内刷新不用再登。
- 遮罩是全屏的，会挡住玩家的点击和触摸，但挡不住键盘操作、自动开始的计时和背景音乐，所以游戏逻辑仍然要等 `onReady` 才启动。这是上架的要求：不要自己隐藏或删除遮罩，不要在 `onReady` 之前让游戏可玩。玩家数只统计通过这个登录进来的人，绕过去的不计数，游戏就上不了首页；平台复查发现被绕过，可以下架。
- 游戏页的地址在登录回来时会短暂带上 `#moky_ticket=…`，脚本会自己处理并从地址栏去掉。如果你的游戏用 `location.hash` 做路由，请忽略以 `moky_ticket=` 开头的 hash。
- 本地预览（localhost 等不是登记地址的页面）时遮罩照常出现，但点登录会被拒绝（地址和登记的不一致），这是正常的；真实效果要发布到登记的地址上看。

### 3.3 发布并自检

按用户项目自己的方式重新发布游戏，然后确认线上页面已经带上脚本和密钥：

```bash
curl -sSL 'https://games.example.com/star-catch/' | grep -o '<script[^>]*clawapps.cn/sdk/moky.js[^>]*>'
```

应该输出那一行脚本的开头标签，且 `data-game` 是你的密钥。如果你有浏览器，再打开页面确认出现了「登录后开始玩」的遮罩；没有浏览器就如实告诉用户「没有在浏览器里实际看过」。

## 4. 准备游戏信息和封面

| 字段 | 要求 |
|---|---|
| 游戏名称 `title` | 1–30 个字。用户没指定时，优先用页面的 `<title>` 或项目名 |
| 一句话介绍 `intro` | 2–200 个字，写清楚玩什么 |
| 分类 `cat` | 只能是其中一个：动作、射击、跑酷、治愈、休闲、策略、解谜、竞速 |
| 封面图 | PNG、JPG 或 WebP，不超过 2 MB。推荐竖版 900×1200（3:4）或横版 1280×720（16:9）；短边不能小于 480 像素、长边不能超过 4096 像素。第一次提交必须有封面 |

封面请用游戏的真实画面：项目里有现成的封面或截图就用它，没有就请用户提供一张。上传封面：

```bash
curl -sS -X POST 'https://clawapps.cn/api/games/cover' \
  -H "Authorization: Bearer $MOKY_TOKEN" \
  -H 'Content-Type: image/png' \
  --data-binary @cover.png
```

`Content-Type` 按图片格式写：PNG 用 `image/png`，JPG 用 `image/jpeg`，WebP 用 `image/webp`。成功返回 `{"ok":true,"cover":"<封面凭证>","w":1280,"h":720,"orient":"landscape"}`。记下 `cover` 的值，下一步要用，只能用一次。

## 5. 提交

方式 A（嵌入）——带上 `"mode":"frame"` 和网址名：

```bash
curl -sS -X POST 'https://clawapps.cn/api/sites/submit' \
  -H "Authorization: Bearer $MOKY_TOKEN" -H 'Content-Type: application/json' \
  -d '{"key":"mk0123456789abcdef","mode":"frame","name":"star-catch","title":"接星星","intro":"接住落下的星星，别碰到陨石。","cat":"休闲","cover":"<封面凭证>"}'
```

方式 B（登录脚本）——不带 `mode` 和 `name`：

```bash
curl -sS -X POST 'https://clawapps.cn/api/sites/submit' \
  -H "Authorization: Bearer $MOKY_TOKEN" -H 'Content-Type: application/json' \
  -d '{"key":"mk0123456789abcdef","title":"接星星","intro":"接住落下的星星，别碰到陨石。","cat":"休闲","cover":"<封面凭证>"}'
```

请求体是 JSON，中文直接写即可（UTF-8）。提交时平台会**当场去访问用户的网站**做检查：

- 方式 A：归属文件在不在、内容是不是这把密钥；游戏页面是否允许被嵌入。
- 方式 B：页面的 HTML 源码里有没有带着这把密钥的登录脚本。

通过就立即收录，不通过会告诉你原因。「收录」之后先是私有状态（不在首页展示），见第 8 节。

成功返回：

```json
{"ok":true,"name":"star-catch","status":"live","url":"https://clawapps.cn/play/star-catch/","public_min":20}
```

- `name`：这款游戏在平台上的名字（查询、删除时用）。方式 A 是你选的网址名，方式 B 是平台生成的 `x-…`。
- `url`：给玩家的地址。方式 A 是平台的统一地址，方式 B 是游戏自己的地址。
- `status` 为 `live` 表示已收录（此时还是私有的，没有公开展示）；`public_min` 是进首页需要的玩家数。

以后要改名称、介绍、分类或封面：用同一个 `key` 和同样的方式再提交一次（不换封面可以不带 `cover`）。平台每次都会重新检查。

## 6. 查看状态和玩家数

```bash
curl -sS 'https://clawapps.cn/api/games/mine' -H "Authorization: Bearer $MOKY_TOKEN"
```

返回 `{"games":[…]}`，按 `name` 找到这一款：`status` 为 `live` 表示已收录，`players` 是玩过的人数，`public` 为 `true` 表示已经在首页展示，`kind` 为 `frame` 表示方式 A、`link` 表示方式 B。返回里还有封面（`cover`、`cw`、`ch`）、更新时间（`updated`）等字段；`version`、`files`、`bytes` 只对云部署的游戏有值，这里是 `null`。

## 7. 出错时怎么办

| error（reason） | 意思 | 怎么办 |
|---|---|---|
| `login_required` | 令牌不对或已过期（7 天） | 按第 0 节重新获取 |
| `bad_url` | 游戏链接不合要求 | 按第 1 节检查 |
| `url_taken` | 这个链接已经被别的账号收录了 | 请用户确认链接；确实是他的就联系平台 |
| `key_not_found` | 密钥不存在，或不是这个账号的 | 用这个账号重新走第 2 节 |
| `proof_missing`（返回里带 `proof_url`） | 方式 A：归属文件取不到 | 确认 `proof_url` 这个地址能打开；回到 3A.1 |
| `proof_mismatch` | 方式 A：归属文件里不是这把密钥 | 把文件内容换成第 2 节领到的密钥后重新发布 |
| `not_embeddable`（`x_frame_options` / `frame_ancestors`） | 方式 A：游戏网站禁止被嵌入 | 按 3A.2 改响应头，或换用方式 B |
| `bad_name` / `name_reserved` / `name_taken` | 方式 A：网址名不合格式、是保留名、或已被占用 | 换一个网址名 |
| `snippet_missing` | 方式 B：页面源码里没有找到登录脚本 | 回到 3B；注意必须写在 HTML 源码里 |
| `snippet_no_key` / `key_mismatch` | 方式 B：脚本上没有密钥，或不是你这把 | 换成第 2 节领到的密钥后重新发布 |
| `fetch_failed`（`dns_failed`） | 域名解析不到 | 检查域名 |
| `fetch_failed` / `proof_missing`（`unreachable` / `tls_failed`） | 连不上，或 HTTPS 证书有问题 | 确认网站在公网能打开、证书有效 |
| `fetch_failed` / `proof_missing`（`http_404` 等 `http_状态码`） | 返回的不是 200 | 确认地址正确、已经发布 |
| `fetch_failed`（`private_address` / `bad_port` / `too_many_redirects`） | 地址指向内网、用了非默认端口、或跳转太多 | 换成公网、默认端口、不绕圈的地址 |
| `bad_title` / `bad_intro` / `bad_cat` | 名称、介绍或分类不合要求 | 按第 4 节改 |
| `cover_required` | 第一次提交没带封面，或封面凭证无效（已用过） | 重新上传封面 |
| `bad_cover` / `cover_size` / `cover_too_large` | 封面格式、尺寸或大小不对 | 换一张图 |
| `too_many` / `too_many_games` | 操作太频繁，或游戏数到上限（每个账号 5 款） | 稍后再试，或请用户先删掉不用的 |

## 8. 完成后告诉用户

1. 游戏已经收录，现在是**私有状态**：不在首页展示。把第 5 节返回的 `url` 发给朋友就能玩；玩家第一次打开要用蒙奇游戏账号登录。
2. 有 20 位玩家玩过之后（开发者自己玩不计入），游戏会出现在蒙奇游戏首页的「新品」里。
3. 在 https://moky.com.cn 右上角的「个人中心」可以看到这款游戏、玩家数、分享二维码，也可以删除。
4. 方式 A：归属文件 `moky-verify.txt` 要一直留在网站上；游戏内容仍在用户自己的网站上，他更新网站，平台上的游戏随之更新。方式 B：登录脚本必须一直留在页面里。去掉之后，平台复查时可以把游戏下架。
5. 你用的是哪种方式、游戏名称、介绍、分类，以及这次有没有在浏览器里实际验证过。

从平台撤下游戏（不会动用户网站上的文件；执行前必须得到用户明确同意）：

```bash
curl -sS -X POST 'https://clawapps.cn/api/games/remove' \
  -H "Authorization: Bearer $MOKY_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"star-catch"}'
```
