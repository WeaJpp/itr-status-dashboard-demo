<div align="center">

# 🚆 工程报验状态仪表盘

## Engineering Inspection Status Dashboard

**为工程报验单（IR / ITR）的日常状态查询而设计，也可以灵活改造成其他需要日常查询、筛选和汇总的网站。**

**Designed for daily Engineering Inspection Request / ITR status tracking, and easily adaptable to other websites that need routine search, filtering, and summary views.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Open_Dashboard-1f7a5a?style=for-the-badge&logo=githubpages&logoColor=white)](https://weajpp.github.io/itr-status-dashboard-demo/)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Deployed-2563a6?style=for-the-badge&logo=github&logoColor=white)](https://weajpp.github.io/itr-status-dashboard-demo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-b58a42?style=for-the-badge)](LICENSE)

![HTML](https://img.shields.io/badge/HTML5-Static-e34f26?logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-Responsive-1572b6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-f7df1e?logo=javascript&logoColor=111)
![Privacy](https://img.shields.io/badge/Data-Synthetic_Only-278466)

[在线演示 / Live Demo](https://weajpp.github.io/itr-status-dashboard-demo/) ·
[核心功能 / Features](#-核心功能--core-features) ·
[快速开始 / Quick Start](#-快速开始--quick-start) ·
[隐私安全 / Privacy](#-隐私与安全--privacy--security)

</div>

---

## 🎯 项目定位 / Purpose

这个项目最初是为工程项目中的**报验单状态查询**而制作的。QA/QC 工程师可以通过一个清晰的网页，快速查看 IR / ITR 总量、审批状态、站点分布，并按编号、工序、站点或里程进行日常查询。

它并不局限于铁路或工程报验。只要业务数据具有“记录编号 + 分类 + 状态 + 日期”这样的结构，就可以复用这套界面。

This project was originally created for **daily engineering inspection-status lookup**. QA/QC teams can use one clear webpage to review IR / ITR totals, approval status, site distribution, and search by record number, activity, site, or chainage.

It is not limited to railway inspection records. Any workflow built around **record ID + category + status + date** can reuse the same interface.

| 中文场景 | English use case |
|---|---|
| 工程报验单、ITR、IR 状态查询 | Engineering inspection, ITR, or IR tracking |
| NCR、RFI、材料报审与文件审批 | NCR, RFI, material submittal, and document approval |
| 设备巡检、缺陷与维修工单 | Equipment inspection, defect, and maintenance tickets |
| 客服工单、订单与售后状态 | Support tickets, orders, and after-sales tracking |
| 任何需要每日搜索和状态汇总的网站 | Any website requiring daily search and status summaries |

> [!NOTE]
> 当前公开版本是一个隐私安全的演示项目。所有站点、编号、数量、日期和里程均为虚构数据，不连接任何真实业务系统。
>
> This public version is a privacy-safe demonstration. All sites, IDs, quantities, dates, and chainages are fictional, with no connection to production systems.

## ✨ 核心功能 / Core Features

- **状态总览 / Status overview** — 汇总 Total、CODE-1、CODE-2、CODE-4、CODE-5、UR 和 DRAFT 等关键状态。
- **站点分布 / Site distribution** — 用紧凑的比例条和计数展示各站点的状态构成。
- **快速查询 / Fast search** — 可按示例 IR 编号、工序、站点、线别或里程即时搜索。
- **组合筛选 / Combined filters** — 支持站点与状态组合筛选，并同步刷新统计卡片和明细表。
- **CSV 导出 / CSV export** — 一键导出当前筛选结果，方便继续分析或发送。
- **响应式界面 / Responsive design** — 兼容桌面和手机，支持浅色、深色主题。
- **零依赖部署 / Zero-dependency deployment** — 纯 HTML、CSS 和 JavaScript，无后端、无数据库、无需构建。

## 🖥️ 在线演示 / Live Demo

### **[https://weajpp.github.io/itr-status-dashboard-demo/](https://weajpp.github.io/itr-status-dashboard-demo/)**

演示数据包括 3 个虚构站点和 14 条虚构 ITR。你可以搜索 `MFBW`、选择站点或筛选状态。

The demo contains 3 fictional sites and 14 fictional ITR records. Try searching for `MFBW`, selecting a site, or filtering by status.

## 🚀 快速开始 / Quick Start

下载仓库后可直接打开 `index.html`，也可以启动本地静态服务：

Download the repository and open `index.html`, or start a local static server:

```bash
git clone https://github.com/WeaJpp/itr-status-dashboard-demo.git
cd itr-status-dashboard-demo
python -m http.server 8000
```

然后访问 / Then open:

```text
http://localhost:8000
```

## 🧩 换成自己的数据 / Use Your Own Data

演示记录位于 [`app.js`](app.js) 顶部的 `SAMPLE_ITRS` 数组：

Demo records are stored in the `SAMPLE_ITRS` array near the top of [`app.js`](app.js):

```js
{
  site: "Demo North",
  process: "Track Laying",
  ir: "DEMO-GQC-IR-00002",
  status: "CODE-2",
  track: "Left",
  chainage: "0+500–1+000",
  updated: "2026-01-14"
}
```

你可以替换字段值、增加记录，或把静态数组改为从已脱敏的 JSON / API 加载。若用于真实项目，应在服务器端处理认证和密钥，不要把密码、Cookie 或 API Token 写入前端。

You can replace values, add records, or load sanitized data from JSON or an API. For production use, handle authentication and secrets on the server—never place passwords, cookies, or API tokens in frontend code.

## 📁 项目结构 / Project Structure

```text
.
├── index.html                  # 页面结构 / Page structure
├── styles.css                 # 视觉与响应式布局 / Responsive styling
├── app.js                     # 模拟数据与交互 / Synthetic data and interactions
├── SECURITY.md                # 安全说明 / Security policy
├── LICENSE                    # MIT License
└── .github/
    └── workflows/
        └── pages.yml           # GitHub Pages 自动部署 / Automatic deployment
```

## 🔐 隐私与安全 / Privacy & Security

- 使用 `Demo` 前缀的虚构站点 / Fictional sites using the `Demo` prefix
- 使用 `DEMO-GQC-IR-xxxxx` 格式的虚构编号 / Fictional record IDs
- 不含真实项目、客户或工程编号 / No real project, customer, or contract identifiers
- 不含密码、Cookie、API Key 或服务账号 / No passwords, cookies, API keys, or service accounts
- 不含 Google Sheet ID、内部链接或生产数据库 / No Sheet IDs, internal URLs, or production databases

> [!IMPORTANT]
> 不要把真实生产数据直接提交到公开仓库。公开前应完成字段脱敏、编号替换、路径清理和凭据扫描。
>
> Never commit production data directly to a public repository. Sanitize fields, replace identifiers, remove local paths, and scan for credentials before publishing.

## 🛠️ 自定义建议 / Customization Ideas

- 将状态名称和颜色改成你的审批流程 / Replace status labels and colors with your approval workflow
- 接入经过认证的只读 API / Connect a secured, read-only API
- 增加日期范围、负责人或标段筛选 / Add date range, owner, package, or discipline filters
- 增加趋势图、逾期提醒和每日自动刷新 / Add trends, overdue alerts, and scheduled refreshes
- 改造成 NCR、RFI、材料报审或工单看板 / Adapt it for NCRs, RFIs, submittals, or service tickets

## 👥 贡献者 / Contributors

| 贡献者 / Contributor | 贡献 / Contribution |
|---|---|
| **[WeaJpp](https://github.com/WeaJpp)** | 项目发起、工程工作流定义与维护 / Project owner, engineering workflow definition, and maintenance |
| **OpenAI Codex** | 界面设计、前端实现、隐私脱敏审计与中英文文档 / UI design, frontend implementation, privacy sanitization audit, and bilingual documentation |

## 🤝 参与贡献 / Contributing

欢迎提交 Issue 或 Pull Request，用于改进可访问性、移动端体验、筛选功能、数据适配器或文档。

Issues and pull requests are welcome, especially for accessibility, mobile UX, filters, data adapters, and documentation.

## 📄 License

本项目采用 [MIT License](LICENSE)，可自由使用、修改和分发。

This project is released under the [MIT License](LICENSE). You may use, modify, and distribute it freely.

---

<div align="center">

**Built for clearer daily inspection tracking · 为更清晰的工程报验日常查询而做**

Made with **OpenAI Codex**

</div>

