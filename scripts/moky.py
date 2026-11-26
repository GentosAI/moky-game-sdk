#!/usr/bin/env python3
"""蒙奇大陆开发者命令行工具（只用 Python 3 标准库）。

用法（先设置令牌：export MOKY_TOKEN="$(python3 scripts/moky.py token)"）：

  python3 scripts/moky.py token                     用手机号 + 密码换令牌（会提示输入，令牌只打印到标准输出）
  python3 scripts/moky.py status                    列出我的游戏、状态和玩家数
  python3 scripts/moky.py cover <图片>              上传封面，输出一次性的封面凭证

  提交游戏链接收录（游戏在你自己的网站上，不改游戏代码，见 docs/integrate.md）：
  python3 scripts/moky.py key <游戏链接>            领取接入密钥；把它写进 moky-verify.txt 放到游戏目录并发布
  python3 scripts/moky.py check <游戏链接> <密钥>   自检：归属文件在不在、网站是否允许被嵌入
  python3 scripts/moky.py submit --key <密钥> --name <网址名> --title <名称> --intro <介绍> --cat <分类> [--cover <图片>]

  免费云部署（把游戏文件交给平台托管，见 docs/deploy.md）：
  python3 scripts/moky.py deploy <产物目录> --name <网址名> --title <名称> --intro <介绍> --cat <分类> [--cover <图片>]

  python3 scripts/moky.py remove <平台上的名字>     从平台撤下一款游戏（需要加 --yes 确认）

令牌只从环境变量 MOKY_TOKEN 读取；本工具不会把令牌或密码写进任何文件。
"""
import argparse, getpass, io, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, zipfile

BASE = os.environ.get("MOKY_API", "https://clawapps.cn/api")
CATS = ["动作", "射击", "跑酷", "治愈", "休闲", "策略", "解谜", "竞速"]
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def token():
    t = os.environ.get("MOKY_TOKEN", "").strip()
    if not t:
        die('没有令牌。先运行：export MOKY_TOKEN="$(python3 scripts/moky.py token)"')
    return t


def call(path, data=None, ctype="application/json", auth=True, query=None, timeout=600):
    """→ (HTTP 状态, 解析后的 JSON)。data 是 dict 时按 JSON 发，是 bytes 时原样发。"""
    url = BASE + path + ("?" + urllib.parse.urlencode(query) if query else "")
    headers = {"User-Agent": "moky-game-sdk/1"}
    if auth:
        headers["Authorization"] = "Bearer " + token()
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode() if isinstance(data, dict) else data
        headers["Content-Type"] = ctype
    req = urllib.request.Request(url, data=body, headers=headers, method="POST" if data is not None else "GET")
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    except urllib.error.URLError as e:
        die(f"连不上 {BASE}：{e.reason}")
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, {"error": "bad_response", "http": status}


def need_ok(status, j, what):
    if status == 200 and (j.get("ok") or "games" in j):
        return j
    reason = f"（{j['reason']}）" if j.get("reason") else ""
    die(f"{what}失败：{j.get('error', 'unknown')}{reason}　HTTP {status}。错误码的意思见 docs/ 里对应指引的「出错时怎么办」。", 2)


def upload_cover(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in MIME:
        die("封面必须是 PNG、JPG 或 WebP")
    with open(path, "rb") as f:
        data = f.read()
    j = need_ok(*call("/games/cover", data, MIME[ext]), "上传封面")
    print(f"封面已上传：{j['w']}×{j['h']}（{'横版' if j.get('orient') == 'landscape' else '竖版'}）", file=sys.stderr)
    return j["cover"]


def cmd_token(a):
    phone = input("蒙奇大陆账号的手机号：") if sys.stdin.isatty() else sys.stdin.readline().strip()
    password = getpass.getpass("密码（不会显示）：") if sys.stdin.isatty() else sys.stdin.readline().rstrip("\n")
    j = need_ok(*call("/auth/token", {"phone": phone.strip(), "password": password}, auth=False), "获取令牌")
    print(f"令牌 {j['expires_in'] // 86400} 天内有效。", file=sys.stderr)
    print(j["token"])


def cmd_status(a):
    j = need_ok(*call("/games/mine"), "查询")
    if not j["games"]:
        print("还没有游戏。")
    for g in j["games"]:
        kind = "链接收录" if g.get("kind") == "frame" else "云部署"
        vis = "已在首页展示" if g.get("public") else f"私有，{g.get('players', 0)}/{g.get('public_min', 20)} 位玩家"
        err = f"　错误：{g['error']}" if g.get("error") else ""
        print(f"{g['name']}\t{g['title']}\t{kind}\t{g['status']}\t{vis}\t{g.get('url') or ''}{err}")


def cmd_cover(a):
    print(upload_cover(a.image))


def cmd_key(a):
    j = need_ok(*call("/sites/key", {"url": a.url}), "领取接入密钥")
    proof = j.get("proof_url") or urllib.parse.urljoin(j["url"], "moky-verify.txt")
    print(f"接入密钥：{j['key']}\n登记的地址：{j['url']}\n\n把密钥写进一个名为 moky-verify.txt 的文本文件，放到游戏入口页所在的目录并发布，使它能通过这个地址访问：\n  {proof}\n\n然后运行 check 自检，再用 submit 提交。")


def cmd_check(a):
    proof = urllib.parse.urljoin(a.url, "moky-verify.txt")
    try:
        text = urllib.request.urlopen(urllib.request.Request(proof, headers={"User-Agent": "moky-game-sdk/1"}), timeout=15).read(4096).decode("utf-8", "replace")
    except (urllib.error.URLError, ValueError) as e:
        die(f"没通过：归属文件打不开 {proof}：{e}", 2)
    if a.key not in text.split():
        die(f"没通过：{proof} 里的内容不是这把密钥。", 2)
    try:
        h = urllib.request.urlopen(urllib.request.Request(a.url, headers={"User-Agent": "moky-game-sdk/1"}), timeout=15).headers
    except (urllib.error.URLError, ValueError) as e:
        die(f"打不开 {a.url}：{e}", 2)
    xfo = (h.get("X-Frame-Options") or "").strip().lower()
    m = re.search(r"frame-ancestors([^;]*)", h.get("Content-Security-Policy") or "", flags=re.I)
    if xfo in ("deny", "sameorigin") or xfo.startswith("allow-from"):
        die(f"没通过：网站用 X-Frame-Options: {xfo} 禁止被嵌入。去掉这个响应头；改不了就改用免费云部署（deploy）。", 2)
    if m and not any(x in ("*", "https:", "https://clawapps.cn") for x in m.group(1).lower().split()):
        die(f"没通过：网站的 frame-ancestors 没有放行 https://clawapps.cn（现在是：{m.group(1).strip()}）。加上它；改不了就改用免费云部署（deploy）。", 2)
    print("通过：归属文件正确，网站允许被嵌入，可以提交了。")


def check_fields(a):
    if not (1 <= len(a.title) <= 30):
        die("名称要 1–30 个字")
    if not (2 <= len(a.intro) <= 200):
        die("介绍要 2–200 个字")
    if a.cat not in CATS:
        die("分类只能是：" + "、".join(CATS))


def cmd_submit(a):
    check_fields(a)
    body = {"key": a.key, "title": a.title, "intro": a.intro, "cat": a.cat}
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,30}", a.name):
        die("网址名要小写字母开头，3–31 位，只含小写字母、数字、连字符")
    body["name"] = a.name
    if a.cover:
        body["cover"] = upload_cover(a.cover)
    j = need_ok(*call("/sites/submit", body), "提交")
    print(f"已收录：{j['name']}　{j['url']}\n现在是私有状态；有 {j.get('public_min', 20)} 位玩家玩过之后会出现在首页的「新品」里。")


def make_zip(root):
    if not os.path.isfile(os.path.join(root, "index.html")):
        die(f"{root} 里没有 index.html。请指向构建产物目录（通常是 dist/）。")
    buf, n = io.BytesIO(), 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x not in (".git", "node_modules")]
            for fn in files:
                if fn == ".DS_Store" or fn.endswith(".map"):
                    continue
                p = os.path.join(d, fn)
                z.write(p, os.path.relpath(p, root).replace(os.sep, "/"))
                n += 1
    data = buf.getvalue()
    if len(data) > 100 * 1024 * 1024:
        die(f"打包后 {len(data) / 1048576:.1f} MB，超过 100 MB 上限。")
    print(f"已打包 {n} 个文件，{len(data) / 1048576:.2f} MB", file=sys.stderr)
    return data


def cmd_deploy(a):
    check_fields(a)
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,30}", a.name):
        die("网址名要小写字母开头，3–31 位，只含小写字母、数字、连字符")
    data = make_zip(a.dir)
    q = {"name": a.name, "title": a.title, "intro": a.intro, "cat": a.cat}
    if a.cover:
        q["cover"] = upload_cover(a.cover)
    need_ok(*call("/games/upload", data, "application/zip", query=q), "上传游戏包")
    print("已进入部署队列，等待上线…", file=sys.stderr)
    t0 = time.time()
    while time.time() - t0 < 300:
        time.sleep(2.5)
        games = need_ok(*call("/games/mine"), "查询")["games"]
        g = next((x for x in games if x["name"] == a.name), None)
        if g and g["status"] not in ("queued", "uploading"):
            if g["status"] == "live" and not g.get("error"):
                print(f"部署成功：{g['url']}\n现在是私有状态：玩家登录后才能玩；有 {g.get('public_min', 20)} 位玩家玩过之后会出现在首页的「新品」里。")
                return
            die(("更新失败，线上仍是上一版：" if g["status"] == "live" else "部署失败：") + str(g.get("error")), 2)
    die("等了 5 分钟还在排队。请稍后用 status 查看，不要重复提交。", 3)


def cmd_remove(a):
    if not a.yes:
        die("撤下后游戏的统一地址会失效。确认请加 --yes。")
    j = need_ok(*call("/games/remove", {"name": a.name}), "撤下")
    print(f"{j['name']}：{j['status']}")


def main():
    ap = argparse.ArgumentParser(description="蒙奇大陆开发者命令行工具", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("token").set_defaults(f=cmd_token)
    sub.add_parser("status").set_defaults(f=cmd_status)
    p = sub.add_parser("cover"); p.add_argument("image"); p.set_defaults(f=cmd_cover)
    p = sub.add_parser("key"); p.add_argument("url"); p.set_defaults(f=cmd_key)
    p = sub.add_parser("check"); p.add_argument("url"); p.add_argument("key"); p.set_defaults(f=cmd_check)
    for name, f in (("submit", cmd_submit), ("deploy", cmd_deploy)):
        p = sub.add_parser(name)
        if name == "deploy":
            p.add_argument("dir"); p.add_argument("--name", required=True)
        else:
            p.add_argument("--key", required=True); p.add_argument("--name", required=True)
        p.add_argument("--title", required=True); p.add_argument("--intro", required=True); p.add_argument("--cat", required=True); p.add_argument("--cover")
        p.set_defaults(f=f)
    p = sub.add_parser("remove"); p.add_argument("name"); p.add_argument("--yes", action="store_true"); p.set_defaults(f=cmd_remove)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
