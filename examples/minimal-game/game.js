// 点点方块：点一下方块得一分。演示怎么等蒙奇游戏登录完成后再让游戏可玩。
(function () {
  var score = 0, box = document.getElementById('box'), start = document.getElementById('start'), msg = document.getElementById('msg');

  function startGame(player) {
    // player.id：这位玩家在你这款游戏里的固定编号（匿名）。可以用它区分玩家、做排行榜。
    start.hidden = true; box.hidden = false; score = 0;
    document.getElementById('score').textContent = score;
  }
  box.addEventListener('click', function () { document.getElementById('score').textContent = ++score; });

  // 2. 等登录完成（Moky.onReady）再启用「开始」；登录脚本没加载成功时给玩家一句提示。
  if (window.Moky) {
    Moky.onReady(function (player) {
      start.disabled = false;
      start.addEventListener('click', function () { startGame(player); });
    });
  } else {
    msg.textContent = '登录组件没有加载成功，请刷新页面重试。';
  }
})();
