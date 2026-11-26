/*! 蒙奇游戏登录 SDK v1 · https://clawapps.cn/integrate.md
 * 用法：<script src="https://clawapps.cn/sdk/moky.js" data-game="你的接入密钥"></script>
 * 作用：玩家没在蒙奇游戏登录时，盖一层「登录后开玩」；登录回来后放行，并告诉游戏玩家是谁。
 *   Moky.onReady(function (player) { ... })   // player.id：这位玩家在你这款游戏里的固定编号（匿名，不是手机号）
 *   Moky.ready / Moky.player                   // 当前状态
 *   window 上会派发 'moky:ready' 事件，event.detail 就是 player */
(function () {
  'use strict';
  if (window.Moky && window.Moky._v) return;
  var API = 'https://clawapps.cn/api/sdk', me = document.currentScript, KEY = me && me.getAttribute('data-game') || '', cbs = [], mask = null;
  var M = window.Moky = { _v: 1, ready: false, player: null, game: KEY,
    onReady: function (f) { if (typeof f !== 'function') return; if (M.ready) f(M.player); else cbs.push(f); },
    login: function () { location.href = API + '/enter?game=' + encodeURIComponent(KEY) + '&back=' + encodeURIComponent(location.href.split('#')[0]); } };
  var SK = 'moky_p_' + KEY;
  function load() { try { var j = JSON.parse(sessionStorage.getItem(SK) || 'null'); return j && j.exp > Date.now() && j.id ? j : null; } catch (e) { return null; } }
  function save(p) { try { sessionStorage.setItem(SK, JSON.stringify(p)); } catch (e) { /* 存不了就每次打开重新登录 */ } }
  function done(p) {
    M.ready = true; M.player = { id: p.id };
    if (mask && mask.parentNode) mask.parentNode.removeChild(mask); mask = null;
    for (var i = 0; i < cbs.length; i++) { try { cbs[i](M.player); } catch (e) { setTimeout(function () { throw e; }); } } cbs = [];
    try { window.dispatchEvent(new CustomEvent('moky:ready', { detail: M.player })); } catch (e) { /* 老浏览器没有 CustomEvent */ }
  }
  function gate(msg) {
    if (mask) { mask.querySelector('p').textContent = msg || ''; return; }
    mask = document.createElement('div');
    mask.setAttribute('style', 'position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;padding:24px;background:rgba(20,28,46,.92);font:16px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;text-align:center');
    mask.innerHTML = '<div style="max-width:320px"><div style="font-size:22px;font-weight:800">登录后开始玩</div><div style="margin-top:8px;color:#c3cad8;font-size:14.5px">这款游戏收录在蒙奇游戏，用蒙奇游戏账号登录就能玩。</div><button type="button" style="margin-top:22px;height:50px;padding:0 34px;border:0;border-radius:999px;background:linear-gradient(180deg,#ffc56e,#ff9a3d);color:#2a1803;font:inherit;font-weight:800;cursor:pointer">登录蒙奇游戏</button><p style="margin:12px 0 0;min-height:20px;color:#ffb4a6;font-size:13px"></p></div>';
    mask.querySelector('button').addEventListener('click', M.login);
    mask.querySelector('p').textContent = msg || '';
    (document.body || document.documentElement).appendChild(mask);
  }
  function start() {
    if (!/^mk[0-9a-f]{16}$/.test(KEY)) { gate('接入有误：脚本上缺少正确的 data-game 接入密钥。'); return; }
    var m = /[#&]moky_ticket=([A-Za-z0-9_-]+)/.exec(location.hash), old = load();
    if (m) {   // 刚从蒙奇游戏登录回来：地址里带着一次性票据，先把它从地址栏拿掉
      try { history.replaceState(null, '', location.href.split('#')[0]); } catch (e) { location.hash = ''; }
      gate('正在确认登录…');
      var x = new XMLHttpRequest();
      x.open('GET', API + '/verify?game=' + encodeURIComponent(KEY) + '&ticket=' + encodeURIComponent(m[1]));
      x.onload = function () { var j = null; try { j = JSON.parse(x.responseText); } catch (e) { /* */ }
        if (j && j.ok && j.player) { var p = { id: j.player.id, exp: Date.now() + (j.expires_in || 43200) * 1000 }; save(p); done(p); }
        else if (old) done(old); else gate('登录已过期，请再点一次。'); };
      x.onerror = function () { if (old) done(old); else gate('网络异常，请再点一次。'); };
      x.send();
    } else if (old) done(old);
    else gate('');
  }
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
})();
