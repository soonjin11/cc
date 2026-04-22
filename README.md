# 巴黎荷风小院 · Le Petit Jardin du Lotus

一个纯静态的单页网站（`index.html`），无构建步骤，直接可部署。

## 本地预览

任选其一：

```bash
# 方式 A：Python
python3 -m http.server 8000
# 打开 http://localhost:8000

# 方式 B：直接在浏览器打开 index.html
```

## 发布到 Vercel

最快的路径（推荐）：

1. 把这个仓库（或这个分支）推到 GitHub。
2. 登录 https://vercel.com → **Add New → Project** → 选这个仓库。
3. 框架预设选 **Other**，Build Command 留空，Output Directory 留空（根目录就是站点）。
4. 点 **Deploy**，约 10 秒后拿到一个 `xxx.vercel.app` 域名。
5. 之后每次 `git push`，Vercel 会自动部署新版本。

也可以用 CLI 本地发布：

```bash
npm i -g vercel
vercel           # 首次会问几个问题，一路回车即可
vercel --prod    # 发布到正式环境
```

## 绑定自定义域名（可选）

在 Vercel 项目 → **Settings → Domains** 添加你的域名，按提示在域名服务商处加一条 CNAME / A 记录即可。

## 结构

```
.
├── index.html   # 整站（HTML + 内联 CSS + 内联 SVG）
└── README.md
```

设计上刻意保持单文件、零依赖，便于快速迭代和替换图片 / 文案。
