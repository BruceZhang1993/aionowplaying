# aionowplaying 官网与 GitHub Pages 设计文档

**日期**: 2026-04-08
**作者**: Codex + Bruce
**状态**: 草案

## 背景

当前仓库已经具备以下对外材料：

- `README.md` 和 `README.zh-CN.md`
- 基于 Sphinx 的文档目录 `docs/`
- Read the Docs 托管的在线文档

但仓库缺少一个更适合作为项目官网入口的页面。现有 Sphinx 首页信息较少，无法很好地承接从 GitHub、PyPI 或搜索引擎进入项目的访客，也没有直接面向 GitHub Pages 的发布流程。

## 目标

为 `aionowplaying` 生成一个可部署到 GitHub Pages 的静态官网，满足以下目标：

1. 官网首页作为文档门户，而不是营销型单页
2. 首页使用英文为主，同时提供清晰的中文入口
3. 复用现有 Sphinx 文档体系，不迁移整套文档工具链
4. 能通过 GitHub Actions 自动构建并发布到 GitHub Pages
5. 站点结构对仓库名路径部署友好，可稳定工作在 Pages 子路径下

## 非目标

本次不包含以下范围：

- 不把整套文档迁移到 MkDocs、Astro、VitePress 等新框架
- 不实现整站双语内容镜像
- 不增加博客、版本切换、全文搜索增强等扩展能力
- 不替换现有 Read the Docs 链接，只把它纳入官网导航体系

## 用户与使用场景

官网主要面向三类访客：

1. 从 GitHub 仓库进入的开发者，需要快速理解项目用途并找到文档
2. 从 PyPI 或搜索结果进入的用户，需要最快看到安装方式和最短示例
3. 中文读者，需要在英文主站下快速找到中文说明入口

这些访客的核心任务不是“浏览品牌故事”，而是“尽快判断是否适合使用并进入文档”。

## 方案选择

评估过三种方向：

1. 纯 Sphinx 门户化改造
2. 独立静态首页 + 现有 Sphinx 文档承接
3. 全站迁移到新的静态站生成器

采用方案 2。

原因：

- 保留现有 Sphinx 文档，避免文档系统迁移成本
- 首页可以脱离 Sphinx 默认观感，做成更像官网的入口页
- GitHub Pages 最终仍只发布静态文件，部署形态简单
- 后续如果需要增强首页，不会影响 API 文档构建链路

## 站点信息架构

最终站点采用如下结构：

- `/`：官网首页，英文主站
- `/docs/`：Sphinx 生成的完整文档
- 外部链接：
  - GitHub 仓库
  - PyPI 项目页
  - 中文 README
  - Read the Docs 文档页

首页不承担所有文档内容，只承担入口和导航职责。深入内容继续由 `/docs/` 提供。

## 首页内容设计

### 1. Hero 区域

首屏展示以下信息：

- 项目名称 `aionowplaying`
- 一句话介绍：跨平台 Python Now Playing client
- 安装命令：`pip install aionowplaying`
- 主按钮：`Read the Docs`
- 次按钮：`View on GitHub`

目标是让首次访问者在几秒内完成三件事：

- 知道项目是做什么的
- 知道如何安装
- 知道下一步去哪里看文档

### 2. Value Proposition 区域

以 3 到 4 个短卡片概括核心能力：

- Cross-platform support
- Automatic backend selection
- Typed playback and metadata models
- Fluent Python API

内容应直接对应仓库现有能力，避免引入文档里没有承诺过的新卖点。

### 3. Platform Support 区域

用三张平台卡片说明支持范围：

- Linux via MPRIS2
- macOS
- Windows

该区域用于强化“一个接口覆盖三端”的项目定位。

### 4. Quick Start 区域

直接展示最短可运行示例代码，复用 README/Quick Start 的现有示例内容，并控制在一屏左右可读范围内。

目标是让访客无需先进入文档，也能立即感知 API 的使用方式。

### 5. Docs Gateway 区域

放置清晰的入口链接：

- Quick Start
- API Reference
- PyPI
- Chinese README
- Read the Docs

这里是首页的核心导航区，优先级高于花哨视觉。

### 6. Footer

展示：

- GPL-3.0-only
- Repository
- Issue Tracker
- Documentation links

## 视觉与交互设计

官网应明显区别于默认 Sphinx 页面，但保持技术项目的克制风格。

设计原则：

- 视觉上更像开源项目官网，而不是文档工具默认模板
- 保持轻量、快速加载、纯静态
- 首页重点突出“入口”和“可信度”，不是复杂动画
- 移动端和桌面端都可读

实现上优先使用原生 HTML/CSS/少量 JavaScript，不引入重型前端框架。

## 技术实现设计

### 首页实现

新增一个轻量静态站点目录，用于存放首页资源，例如：

```text
site/
  index.html
  assets/
    styles.css
    script.js
```

首页资源应采用相对路径或兼容 GitHub Pages 子路径的资源引用方式，避免因仓库名路径导致静态资源 404。

### 文档构建

继续使用现有 Sphinx 配置构建文档：

```shell
sphinx-build -b html docs <output>/docs
```

最终 Pages 发布目录中：

- 首页文件位于根目录
- Sphinx 文档输出到 `docs/` 子目录

这样首页链接到 `/docs/` 时结构清晰，也与信息架构一致。

### 构建产物汇总

增加一个构建步骤，将首页和 Sphinx 文档汇总到单一发布目录，例如：

```text
dist/
  index.html
  assets/
  docs/
```

GitHub Pages 只发布该目录内容。

## GitHub Pages 部署设计

新增 GitHub Actions workflow，职责如下：

1. 检出仓库代码
2. 安装 Python 和文档依赖
3. 构建 Sphinx 文档
4. 复制首页静态资源到发布目录
5. 上传 Pages artifact
6. 发布到 GitHub Pages

建议使用 GitHub 官方 Pages 工作流能力，而不是手动 push 到 `gh-pages` 分支。这样更符合当前 GitHub Pages 的标准部署方式，也更易维护。

## 仓库改动范围

预计会涉及以下改动：

- 新增官网首页静态资源目录
- 新增构建输出汇总脚本或简单命令流程
- 新增 GitHub Pages workflow
- 视需要补充 `README` 中的官网/部署说明

现有 Python 包代码和运行时逻辑不在本次改动范围内。

## 测试与验证

实现完成后需要验证以下内容：

1. 首页本地可直接打开并正常显示
2. Sphinx 文档可正常构建到目标目录
3. 汇总后的站点目录结构正确
4. 首页到 `/docs/` 的导航可用
5. GitHub Pages workflow 语法正确，部署目标符合 GitHub Pages 规范
6. 在仓库名子路径场景下，CSS/JS/链接不因绝对路径失效

## 风险与处理

### 路径风险

GitHub Pages 项目站点通常部署在 `/<repo-name>/` 子路径下。如果首页静态资源使用根绝对路径，容易出现资源丢失。

处理方式：静态资源统一使用相对路径，内部导航也避免对根路径做错误假设。

### 文档与官网风格割裂

首页与 Sphinx 页面会天然存在风格差异。

处理方式：不强行统一成同一套设计语言，只保证信息架构清晰、跳转顺畅。此次优先解决“有没有官网”和“能否部署”。

### 双语维护成本

如果首页也做整站双语，将带来额外维护负担。

处理方式：保持英文主站，只提供中文 README / 中文文档入口。

## 实施结果预期

完成后，仓库将具备：

- 一个可作为项目官网入口的英文首页
- 一个通过 GitHub Pages 可持续发布的静态站
- 一个和现有 Sphinx 文档协同工作的文档门户结构
- 一个面向中文读者的清晰入口，而不增加整站双语维护成本
