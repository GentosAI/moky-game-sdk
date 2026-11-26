# 接入示例：点点方块

一个已经接好蒙奇游戏登录的最小游戏，只有两个文件：

- `index.html`：`<head>` 里那一行 `<script src="https://clawapps.cn/sdk/moky.js" data-game="…">` 就是全部的页面改动。
- `game.js`：`Moky.onReady(...)` 之后才启用「开始」按钮。

`data-game="mk0000000000000000"` 是占位符，不能直接用。接入你自己的游戏时，按 [`docs/integrate.md`](../../docs/integrate.md) 领取你自己的接入密钥并替换。

本地直接打开这个页面会看到「登录后开始玩」的遮罩，并提示密钥不对或点登录被拒绝——这是正常的：登录只在你登记的线上地址上生效。
