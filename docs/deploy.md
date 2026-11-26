# 蒙奇大陆 · 免费云部署指引（给 AI 编程助手）

你正在帮用户把一款单机网页游戏部署到蒙奇大陆（clawapps.cn）。请按顺序执行，每一步完成后再做下一步。

通用约定：

- 所有接口返回 JSON，请用 JSON 解析后判断，不要做字符串匹配。
- 成功时 HTTP 状态是 200 且带 `"ok":true`（查询接口直接返回数据）；失败时 HTTP 状态是 4xx / 5xx，返回 `{"error":"错误码"}`，错误码的意思见第 8 节。
- 如果用户不在场、没法回答问题：游戏信息按要求自己拟定，直接部署，完成后把你用的信息一并告诉用户。

## 0. 获取令牌

部署需要用户的蒙奇大陆账号（在 https://clawapps.cn 右上角用手机号注册）。用手机号和密码换一个令牌，之后的每一步都带这个令牌，7 天内有效：

```bash
curl -sS -X POST 'https://clawapps.cn/api/auth/token' \
  -H 'Content-Type: application/json' \
  -d '{"phone":"用户的手机号","password":"用户的密码"}'
```

成功返回 `{"ok":true,"token":"clt_…","expires_in":604800}`。把 `token` 放进环境变量，后面的命令都用它：

```bash
export MOKY_TOKEN='clt_…'
```

注意：

- 手机号和密码请向用户要，或者请用户自己运行上面这条命令、只把返回的令牌给你（推荐：用户在你运行命令的同一个终端里先执行 `export MOKY_TOKEN=…`；如果用户给的是一个存着令牌的文件，只把它读进环境变量，不要复制、不要改动）。
- 密码和令牌都不要写进任何文件、不要提交到代码仓库、不要打印到日志里。
- 返回 `bad_login`：手机号或密码不对，或者这个号还没注册，请用户核对。返回 `too_many`：尝试太多次，等 15 分钟再试。

## 1. 确认游戏符合要求

逐条检查，不符合的先改好：

| 项 | 要求 |
|---|---|
| 类型 | 纯静态的单机网页游戏。不支持服务端程序，包里的任何程序都不会被执行。 |
| 入口 | 产物根目录必须有 `index.html`。 |
| 路径 | 全部使用相对路径（`./js/main.js`、`assets/a.png`）。以 `/` 开头的路径会加载不到。用 Vite 构建的把 `base` 设成 `'./'`，其他构建工具同理。 |
| 隔离环境 | 游戏页带响应头 `Content-Security-Policy: sandbox allow-scripts allow-pointer-lock allow-forms allow-modals allow-orientation-lock`，页面来源是匿名来源。 |
| 读自己的文件 | 脚本、ES module、wasm、`fetch` / XHR 读包里的 JSON、图片、音频、模型都正常，条件是：用相对路径；`fetch` 不要带 `credentials: 'include'`；标签上不要加 `crossorigin="use-credentials"`（不加或 `anonymous` 都行）。 |
| 可以用 | `alert` / `confirm`、表单提交、鼠标锁定、锁定横屏。 |
| 弹窗和跳转 | `window.open` 和 `target="_blank"` 的链接不可用。游戏里不要做跳转和弹窗，外部链接不保证可用。 |
| 本站接口 | 游戏里调用 clawapps.cn 的 `/api/` 会被浏览器拦下，不要依赖。 |
| 本地存储 | 在隔离环境里访问 `localStorage`、`sessionStorage`、`document.cookie`、`IndexedDB` 会抛 `SecurityError`。所有访问都要包上 `try / catch`，存档只能留在内存里。 |
| 后台线程 | `new Worker('worker.js')` 这种写法在隔离环境里会失败，要用 Blob 方式创建。 |
| 外部请求 | 不要依赖任何外部接口、CDN、外链字体或统计脚本，所有依赖都打进包里。 |
| 大小 | zip 不超过 100 MB；解开后不超过 400 MB、5000 个文件，单个文件不超过 100 MB。 |

如果项目需要构建，先执行构建，部署的是构建产物目录（通常是 `dist/`）。

## 2. 本地自检

在产物目录里起一个静态服务器，把它放在一个子路径下访问（模拟线上的 `/play/<网址名>/`），确认游戏能打开、能开始玩、控制台没有报错、没有请求发往别的域名。例如：

```bash
mkdir -p /tmp/moky-check/play && ln -sfn "$PWD/dist" /tmp/moky-check/play/my-game
(cd /tmp/moky-check && python3 -m http.server 8765)   # 然后访问 http://127.0.0.1:8765/play/my-game/
```

如果你没有浏览器可用：至少确认入口页和它引用的每个文件都能取到（HTTP 200），并通读代码检查第 1 节的各项；然后如实告诉用户「没有在浏览器里实际玩过」。

## 3. 准备游戏信息和封面

向用户确认或自己拟定后请用户过目：

| 字段 | 要求 |
|---|---|
| 网址名 `name` | 小写字母开头，3–31 位，只含小写字母、数字、连字符。游戏地址就是 `https://clawapps.cn/play/<name>/`。同一个账号用同一个网址名再次部署 = 更新。 |
| 游戏名称 `title` | 1–30 个字。 |
| 一句话介绍 `intro` | 2–200 个字，写清楚玩什么。 |
| 分类 `cat` | 只能是其中一个：动作、射击、跑酷、治愈、休闲、策略、解谜、竞速。 |
| 封面图 | PNG、JPG 或 WebP，不超过 2 MB。推荐竖版 900×1200（3:4）或横版 1280×720（16:9）；不要求尺寸完全一致，但短边不能小于 480 像素、长边不能超过 4096 像素，比例偏离时页面会居中裁切。第一次部署必须有封面；更新时不换封面可以不传。 |

封面请用游戏的真实画面：项目里有现成的封面或截图就用它，没有就请用户提供一张，或者在本地运行游戏后截一张图。封面是单独上传的，不需要放进游戏包（放了也不影响）。

## 4. 打包

在产物目录里打包，保证 `index.html` 在 zip 的根目录：

```bash
cd dist && zip -r ../game.zip . -x '*.map' -x '.DS_Store' && cd ..
```

## 5. 上传封面

```bash
curl -sS -X POST 'https://clawapps.cn/api/games/cover' \
  -H "Authorization: Bearer $MOKY_TOKEN" \
  -H 'Content-Type: image/png' \
  --data-binary @cover.png
```

`Content-Type` 按图片格式写：PNG 用 `image/png`，JPG 用 `image/jpeg`，WebP 用 `image/webp`。

成功返回 `{"ok":true,"cover":"<封面凭证>","w":1280,"h":720,"orient":"landscape"}`（`w`、`h` 是识别到的宽高，`orient` 是横版 `landscape` 或竖版 `portrait`）。记下 `cover` 的值，下一步要用，只能用一次。

## 6. 上传游戏包

中文参数必须做 URL 编码，用 `--data-urlencode` 配合 `-G` 不行（这里 body 是 zip），所以请先把参数编码好再拼进地址。例如用 Python 生成查询串：

```bash
QS=$(python3 -c "import urllib.parse,sys;print(urllib.parse.urlencode({'name':sys.argv[1],'title':sys.argv[2],'intro':sys.argv[3],'cat':sys.argv[4],'cover':sys.argv[5]}))" \
  'star-catch' '接星星' '接住落下的星星，别碰到陨石。' '休闲' '<封面凭证>')

curl -sS -X POST "https://clawapps.cn/api/games/upload?$QS" \
  -H "Authorization: Bearer $MOKY_TOKEN" \
  -H 'Content-Type: application/zip' \
  --data-binary @game.zip
```

成功返回 `{"ok":true,"task":"…","name":"…","status":"queued"}`，表示已进入部署队列。`task` 是这次部署的任务号，只在向平台反馈问题时有用，后面的步骤用不到。

## 7. 等部署完成

每 2–3 秒查一次，直到这款游戏的 `status` 不再是 `queued`。小包几秒钟就好，几十 MB 的大包要一两分钟；等满 5 分钟还是 `queued` 再告诉用户稍后到创作中心查看，不要提前判定失败，也不要重复提交：

```bash
curl -sS 'https://clawapps.cn/api/games/mine' -H "Authorization: Bearer $MOKY_TOKEN"
```

返回的是这个账号下的全部游戏，按 `name` 找到你刚提交的那一条（提交成功后它一定在列表里）：

```json
{"games":[{"name":"star-catch","title":"接星星","intro":"…","cat":"休闲","status":"live",
  "url":"https://clawapps.cn/play/star-catch/","version":"20261125223610-239b5a99","files":5,"bytes":28071,
  "error":null,"cover":"/assets/landing/ugc/star-catch.18498956.png","cw":1280,"ch":720,"updated":1795646173,"slow":false}]}
```

`files`、`bytes` 是部署后的文件数和占用的磁盘空间（每个文件至少占 4 KB，所以会比源文件合计和 zip 都大，属正常；解开后 400 MB 的上限按这个数算）；`cover`、`cw`、`ch` 是封面地址和宽高；`slow` 为 `true` 表示排队超过 10 分钟；部署失败的原因在 `error` 里，成功时 `error` 是 `null`。

- `status` 为 `live` 且 `error` 为 `null`：部署成功，`url` 就是游戏地址。
- `status` 为 `failed`，或者 `live` 但带 `error`（更新失败，线上仍是上一版）：按下面的表处理。

## 8. 出错时怎么办

错误码有两个来源：第 5、6 节的接口直接返回（HTTP 4xx / 5xx）；或者包已经收下、部署时才发现问题，出现在第 7 节那条记录的 `error` 字段里。

| error | 意思 | 怎么办 |
|---|---|---|
| `login_required` | 令牌不对或已过期（7 天） | 按第 0 节重新获取令牌 |
| `bad_name` | 网址名不合格式 | 按第 3 节改 |
| `name_reserved` / `name_taken` | 网址名是保留名，或被别人用了 | 换一个 |
| `bad_title` / `bad_intro` / `bad_cat` | 名称、介绍或分类不合要求 | 按第 3 节改 |
| `cover_required` | 第一次部署没带封面，或封面凭证无效（已用过） | 重新上传封面 |
| `bad_cover` / `cover_size` / `cover_too_large` | 封面格式、尺寸或大小不对 | 换一张图 |
| `not_a_zip` / `bad_zip` | 不是 zip 或 zip 损坏 | 重新打包 |
| `too_large` / `zip_too_large` / `too_many_files` | 超过大小或文件数上限 | 精简资源 |
| `no_index_html` | zip 根目录没有 index.html | 在产物目录里面打包 |
| `busy` | 这款游戏上一次部署还没结束 | 等一会儿再试 |
| `too_many` / `too_many_games` | 今天提交太多，或游戏数到上限（每个账号 5 款） | 明天再试，或请用户先删掉不用的 |
| `run_failed` / `health_check_failed` / `nginx_test_failed` / `transfer_failed` / `queue_unavailable` | 平台问题 | 告诉用户稍后重试，不要反复提交 |

## 9. 完成后

1. 确认游戏已上线：以第 7 节的 `status` 为准。游戏地址需要登录才能打开，你直接请求它会被转到登录页（HTTP 302），这是正常的，不代表部署失败。
2. 告诉用户：游戏地址、网址名、这次用的名称和介绍。
3. 提醒用户：以后更新，用同一个网址名再部署一次即可；删除游戏在 clawapps.cn 右上角的「创作中心」里操作。
4. 告诉用户游戏现在是私有状态：玩家需要先登录蒙奇大陆账号才能打开游戏地址（没登录会被带去登录，登录后自动进入）；有 20 位玩家玩过之后，游戏会出现在 clawapps.cn 首页的「新品」里。开发者自己玩不计入人数。

删除也可以用命令（会让游戏地址立刻失效，执行前必须得到用户明确同意）：

```bash
curl -sS -X POST 'https://clawapps.cn/api/games/remove' \
  -H "Authorization: Bearer $MOKY_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"star-catch"}'
```
