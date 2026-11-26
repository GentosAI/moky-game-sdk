# 蒙奇大陆 · 提交游戏链接收录指引（给 AI 编程助手）

你正在帮用户把一款**已经放在他自己网站上的网页游戏**收录到蒙奇大陆（clawapps.cn）。收录后：

- 游戏得到一个统一的地址 `https://clawapps.cn/play/<网址名>/`：这是平台的页面，玩家登录后把游戏嵌在里面。**游戏代码一行都不用改**，你只需要在游戏网站上放一个小文本文件；
- 玩家用蒙奇大陆账号登录后才能玩，平台由此统计有多少位玩家玩过；
- 游戏先是私有状态，有 20 位玩家玩过之后，出现在蒙奇大陆首页的「新品」里。

如果用户没有自己的网站、只是想把游戏文件交给平台托管，请改看另一份文档：https://clawapps.cn/deploy.md 。几条路选一条即可：同一款游戏做多次，平台上会出现多条互不相干的记录，玩家数分开算。

前提：游戏网站没有禁止被别的网站嵌入（第 3.2 节会检查）。如果禁止且改不了，这款游戏不能用这种方式收录，请改用免费云部署（上面那份文档）。

请按顺序执行，每一步完成后再做下一步。

通用约定：

- 所有接口返回 JSON，请用 JSON 解析后判断，不要做字符串匹配。
- 成功时 HTTP 状态是 200 且带 `"ok":true`；失败时 HTTP 状态是 4xx / 5xx，返回 `{"error":"错误码"}`，有的还带 `"reason"`，意思见第 7 节。
- 如果用户不在场、没法回答问题：游戏信息按要求自己拟定，直接做完，完成后把你用的信息一并告诉用户。

## 0. 获取令牌

接入需要用户的蒙奇大陆账号（在 https://moky.com.cn 右上角用手机号注册）。用手机号和密码换一个令牌，之后的每一步都带这个令牌，7 天内有效：

```bash
curl -sS -X POST 'https://clawapps.cn/api/auth/token' \
  -H 'Content-Type: application/json' \
  -d '{"phone":"用户的手机号","password":"用户的密码"}'
```

成功返回 `{"ok":true,"token":"clt_…","expires_in":604800}`。把 `token` 放进环境变量：

```bash
export MOKY_TOKEN='clt_…'
```

- 手机号和密码请向用户要，或者请用户自己运行上面这条命令、只把返回的令牌给你（推荐：用户在你运行命令的同一个终端里先执行 `export MOKY_TOKEN=…`；如果用户给的是一个存着令牌的文件，用 `export MOKY_TOKEN="$(cat 文件路径)"` 读进环境变量，不要复制、不要改动。如果你的每条命令是在新的 shell 里运行的，环境变量不会保留，每次都要重新读一遍）。
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
 "proof_url":"https://games.example.com/star-catch/moky-verify.txt"}
```

- `key` 是这个账号、这个链接专用的接入密钥，同一个链接再领一次还是同一把。密钥不是秘密。
- `url` 是平台整理后的地址，后面以它为准。
- `proof_url` 是下一步那个归属文件应该能被访问到的地址。

## 3. 放归属文件并自检

### 3.1 放一个归属文件

在游戏入口页**所在的目录**下放一个名为 `moky-verify.txt` 的文本文件，内容就是第 2 节领到的密钥（一行）：

```bash
echo 'mk0123456789abcdef' > moky-verify.txt   # 放在和游戏的 index.html 同一个目录
```

文件里只要有这一行密钥即可，结尾的换行、Windows 换行都没关系。然后按用户项目自己的方式重新发布，让它能通过网址访问。文件的地址是「游戏地址所在目录 + `moky-verify.txt`」，例如游戏地址是 `https://games.example.com/star-catch/`，文件就是 `https://games.example.com/star-catch/moky-verify.txt`；游戏地址是 `https://games.example.com/play.html`，文件就是 `https://games.example.com/moky-verify.txt`。

这个文件用来证明网站是用户自己的。它不影响游戏，上架后也请一直留着。用构建工具的项目，把它放进会原样拷贝到产物里的目录（例如 Vite 的 `public/`）。

### 3.2 自检

```bash
# 归属文件能访问，内容是密钥
curl -sSL 'https://games.example.com/star-catch/moky-verify.txt'

# 游戏页面没有禁止被嵌入（用 GET 取响应头，只看最后一次响应）
curl -sSL -o /dev/null -D - 'https://games.example.com/star-catch/' | grep -iE '^(x-frame-options|content-security-policy):' || true
```

第二条命令**没有输出最好**（没有匹配时 `grep` 的退出码是 1，属于正常，所以后面加了 `|| true`）。有跳转时会打印每一跳的响应头，以最后一跳为准。如果输出里有 `X-Frame-Options: DENY` / `SAMEORIGIN`，或者 `Content-Security-Policy` 里有 `frame-ancestors` 且没有放行 `https://clawapps.cn`，说明网站禁止被嵌入，提交会被拒绝（`not_embeddable`）。这时二选一：

- 用户能改网站的响应头：去掉 `X-Frame-Options`，或者把 `frame-ancestors` 改成包含 `https://clawapps.cn`，然后继续；
- 改不了：告诉用户这款游戏不能用提交链接的方式收录，可以改用免费云部署（https://clawapps.cn/deploy.md）。

游戏在嵌入环境里运行时：自己的本地存档、自己域名下的接口都照常可用；不能把整个浏览器页面跳转到别处（`top.location`）；全屏、手柄、陀螺仪可以用。

### 3.3 选一个网址名

网址名 `name`：小写字母开头，总长度 3–31 位，只含小写字母、数字、连字符。游戏的统一地址就是 `https://clawapps.cn/play/<name>/`。用户没指定时，用项目名或游戏英文名拟一个。

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

```bash
curl -sS -X POST 'https://clawapps.cn/api/sites/submit' \
  -H "Authorization: Bearer $MOKY_TOKEN" -H 'Content-Type: application/json' \
  -d '{"key":"mk0123456789abcdef","name":"star-catch","title":"接星星","intro":"接住落下的星星，别碰到陨石。","cat":"休闲","cover":"<封面凭证>"}'
```

请求体是 JSON，中文直接写即可（UTF-8）。提交时平台会**当场去访问用户的网站**做检查：归属文件在不在、内容是不是这把密钥；游戏页面是否允许被嵌入。

通过就立即收录，不通过会告诉你原因。「收录」之后先是私有状态（不在首页展示），见第 8 节。

提交前建议先按第 6 节看一眼账号下已有的游戏：每个账号最多 5 款；游戏名称允许重复，但同一款游戏不要重复收录。请求体里有引号等特殊字符时，可以把 JSON 写进临时文件再用 `-d @文件` 发送（文件里不要有令牌，用完删掉）。

成功返回：

```json
{"ok":true,"name":"star-catch","status":"live","url":"https://clawapps.cn/play/star-catch/","public_min":20}
```

- `name`：这款游戏在平台上的名字，就是你选的网址名（查询、删除时用）。
- `url`：给玩家的统一地址。
- `status` 为 `live` 表示已收录（此时还是私有的，没有公开展示）；`public_min` 是进首页需要的玩家数。

以后要改名称、介绍、分类或封面：用同一个 `key` 和同一个 `name` 再提交一次（不换封面可以不带 `cover`）。平台每次都会重新检查。

## 6. 查看状态和玩家数

```bash
curl -sS 'https://clawapps.cn/api/games/mine' -H "Authorization: Bearer $MOKY_TOKEN"
```

返回 `{"games":[…]}`，按 `name` 找到这一款：`status` 为 `live` 表示已收录，`players` 是玩过的人数，`public` 为 `true` 表示已经在首页展示，`kind` 为 `frame` 表示通过链接收录的游戏、`deploy` 表示云部署的游戏。其余字段：`title`、`intro`、`cat` 是提交的信息；`cover`、`cw`、`ch` 是封面地址和宽高；`updated` 是更新时间；`public_min` 是进首页需要的玩家数；`error` 没有错误时是 `null`；`slow` 只对云部署有意义（排队超过 10 分钟为 `true`）；`version`、`files`、`bytes` 只对云部署的游戏有值，这里是 `null`。

没有浏览器时的最小验证：不登录直接请求统一地址，应当得到 HTTP 302，跳到 `https://clawapps.cn/?login=1&next=/play/<网址名>/`，这说明外壳页已经生效、登录拦截在起作用。

## 7. 出错时怎么办

| error（reason） | 意思 | 怎么办 |
|---|---|---|
| `login_required` | 令牌不对或已过期（7 天） | 按第 0 节重新获取 |
| `bad_url` | 游戏链接不合要求 | 按第 1 节检查 |
| `url_taken` | 这个链接已经被别的账号收录了 | 请用户确认链接；确实是他的就联系平台 |
| `key_not_found` | 密钥不存在，或不是这个账号的 | 用这个账号重新走第 2 节 |
| `proof_missing`（返回里带 `proof_url`） | 归属文件取不到 | 确认 `proof_url` 这个地址能打开；回到 3.1 |
| `proof_mismatch` | 归属文件里不是这把密钥 | 把文件内容换成第 2 节领到的密钥后重新发布 |
| `not_embeddable`（`x_frame_options` / `frame_ancestors`） | 游戏网站禁止被嵌入 | 按 3.2 改响应头；改不了就改用免费云部署 |
| `bad_name` / `name_reserved` / `name_taken` | 网址名不合格式、是保留名、或已被占用 | 换一个网址名 |
| `fetch_failed`（`dns_failed`） | 域名解析不到 | 检查域名 |
| `fetch_failed` / `proof_missing`（`unreachable` / `tls_failed`） | 连不上，或 HTTPS 证书有问题 | 确认网站在公网能打开、证书有效 |
| `fetch_failed` / `proof_missing`（`http_404` 等 `http_状态码`） | 返回的不是 200 | 确认地址正确、已经发布 |
| `fetch_failed`（`private_address` / `bad_port` / `too_many_redirects`） | 地址指向内网、用了非默认端口、或跳转太多 | 换成公网、默认端口、不绕圈的地址 |
| `bad_title` / `bad_intro` / `bad_cat` | 名称、介绍或分类不合要求 | 按第 4 节改 |
| `cover_required` | 第一次提交没带封面，或封面凭证无效（已用过） | 重新上传封面 |
| `bad_cover` / `cover_size` / `cover_too_large` | 封面格式、尺寸或大小不对 | 换一张图 |
| `too_many` / `too_many_games` | 操作太频繁，或游戏数到上限（每个账号 5 款） | 稍后再试，或请用户先删掉不用的 |

## 8. 完成后告诉用户

1. 游戏已经收录，现在是**私有状态**：不在首页展示。把第 5 节返回的 `url` 发给朋友就能玩；玩家第一次打开要用蒙奇大陆账号登录。
2. 有 20 位玩家玩过之后（开发者自己玩不计入），游戏会出现在蒙奇大陆首页的「新品」里。
3. 在 https://moky.com.cn 右上角的「创作中心」可以看到这款游戏、玩家数、分享二维码，也可以删除。
4. 归属文件 `moky-verify.txt` 要一直留在网站上，去掉之后平台复查时可以把游戏下架。游戏内容仍在用户自己的网站上，他更新网站，平台上的游戏随之更新。
5. 你用的游戏名称、网址名、介绍、分类，以及这次有没有在浏览器里实际验证过。

从平台撤下游戏（不会动用户网站上的文件；执行前必须得到用户明确同意）：

```bash
curl -sS -X POST 'https://clawapps.cn/api/games/remove' \
  -H "Authorization: Bearer $MOKY_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"star-catch"}'
```
