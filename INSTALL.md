# 玉书房官网 修复包 v3（三语版）｜2026-09-12

---

# 第一步：解压

**下载到的是 .zip，必须先解压再上传。**直接把 zip 拖进 GitHub，只会在仓库里多一个压缩包文件，网站不会有任何变化。

Windows：右键点这个 zip → **全部解压缩** → 解压 → 得到一个文件夹，里面是下面这些东西。

```
_config.yml        _drafts/        about.md        index.html
_includes/         _en/            advisors.md     llms.txt
_layouts/          _fr/            essays.md       INSTALL.md
_posts/            en/             fr/
```

---

# 第二步：填订阅表单 ID

1. kit.com 注册（免费版，10,000 订阅者上限）
2. 后台 Grow → Landing Pages & Forms → Create New → Form → Inline
3. 建好后在嵌入代码或网址里找到一串数字，例如 `8123456`
4. 用记事本打开解压出来的 `index.html`，Ctrl+F 搜 `KIT_FORM_ID`，**两处**都换成那串数字
5. 保存

不填这一步，订阅按钮依然是坏的。这是全包唯一需要你手填的地方。

---

# 第三步：上传

1. 打开 https://github.com/CharlieThomasMunger/yushufang
2. 点 **Add file** → **Upload files**
3. 打开解压出来的文件夹，**全选里面所有文件和文件夹**（Ctrl+A），拖进 GitHub 页面那块虚线区域
   - 一定要选文件夹里的内容，不要把最外层那个文件夹整个拖进去，否则会多一层目录
   - 以下划线开头的 `_layouts` `_includes` `_drafts` `_posts` `_en` `_fr` 一个都不能漏
4. 下方 commit 说明填：`fix: trilingual structure, nav, subscribe form, article system`
5. 点 **Commit changes**

覆盖的：`index.html`、`_config.yml`、`about.md`、`advisors.md`、`llms.txt`
新增的：其余全部

GitHub Pages 会自动重新构建，**约 1–3 分钟**生效。构建状态在仓库首页 commit 记录旁边那个小圆点：转圈=构建中，绿勾=成功，红叉=失败（把报错截图发我）。

---

# 第四步：验证

构建完成后逐条点：

- [ ] yushufang.org 首页顶部有「首页 · 文章 · 关于」，右侧有「中 EN FR」
- [ ] 点「文章」进得去 /essays/，不是 404
- [ ] 点「关于」，履历有内容，不是方括号
- [ ] 点 EN 进 /en/，点 FR 进 /fr/，都能打开
- [ ] 首页填邮箱点订阅，Kit 后台能看到这个订阅者
- [ ] /sitemap.xml 和 /feed.xml 都能正常打开
- [ ] 导航里没有 For Advisors（直接访问 /advisors/ 仍在）

---

# 三语架构（已定，不要改）

| 版本 | 路径 | 角色 | 内容量 |
|---|---|---|---|
| 中文 | `/` | 主站，思想母体 | 全量 |
| 英文 | `/en/` | 顾问与机构 | 精选 |
| 法文 | `/fr/` | 本地可信度门面 | 一页，不设文章流 |

- 用子目录不用子域名：域名权重不分家，不必动 DNS
- 三个首页都带 hreflang，搜索引擎知道它们是同一内容的不同语言版本，不会判成重复内容
- 语言切换在导航右侧，任何页面都能切
- 英文文章放 `_en/`，自动出现在 /en/essays/。法文暂不设文章流，`_fr/` 是预留

**中文是唯一的全量版本。**英文法文是子集，不是翻译镜像——不要把每篇中文文章都翻三遍，那是一年 156 篇，会吃掉母体预算。

## 英文法文页当前是 noindex

`/en/` `/en/about/` `/en/essays/` `/fr/` 四个页面的 front matter 里都有一行 `noindex: true`。

这是故意的：**外语文案需要你过一遍再让搜索引擎收录。**

你读完觉得可以，就把这四个文件里的 `noindex: true` 删掉，重新提交。中文主站不受影响，现在就是正常收录状态。

---

# 以后怎么发文章

**中文：**
1. 复制 `_drafts/TEMPLATE.md`
2. 填 front matter（`book_candidate` 和 `content_origin` 必填）
3. 写正文
4. 改名成 `2026-09-20-slug.md`，移到 `_posts/`
5. 提交，自动出现在 /essays/、sitemap、RSS

**英文：**同样的模板，改 `lang: en`，放进 `_en/`，自动出现在 /en/essays/

---

# 名字的主次（已定）

站点正名只有一个：**玉书房**。标签栏、搜索结果、RSS 都只出现这三个字。

- **The Jade Study** —— 只在英文块、For Advisors、页脚落款、英文页
- **Yushufang** —— 拼音与域名对应，写在 llms.txt 和结构化数据里

两者都写进了 schema 的 `alternateName`，搜索引擎和 AI 知道它们指同一实体，但中文读者不会被占用注意力。

---

# 这次没做、留给下一轮

- 七个核心概念页（/concepts/...）—— 冻结的第一优先级
- 六域 Hub 页（/decisions/education/ 等）
- 判断档案
- CSS 合并（现在首页和内页各自内联，重复约 60 行）。故意没做：容器里无法构建预览，改动越大越可能把线上改花
- Google Search Console 提交 sitemap
- 首页第一屏那块英文 lockup 是否保留（属冻结的定位区，等你决定）
