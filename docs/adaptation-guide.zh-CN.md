# 报验单检测系统接入教程

本项目支持两种接入方式。无论使用哪一种，都必须先确认你有权访问和自动查询目标网站。第一阶段只读，不修改台账、不提交表单、不下载未授权附件。

## 方法 A：自己分析 HTML 或 API

### 1. 准备一个最小测试范围

从台账复制 1–3 个非敏感测试编号，确认人工查询能找到结果。不要一开始就全量运行。

### 2. 优先识别查询 API

1. 登录目标网站，打开浏览器开发者工具。
2. 进入 `Network`，选择 `Fetch/XHR`，清空旧请求。
3. 手动搜索一个测试编号。
4. 查找刚出现的请求，记录请求方法、参数名、分页方式及响应结构。
5. 确认响应内哪个字段是报验编号、最终状态、提交时间和生命周期。

只记录接口结构，不要把 `Authorization`、Cookie、密码或真实响应提交到 GitHub。认证值应由环境变量提供。

如果网站允许附件下载，在 Network 中点击一次获授权的下载按钮，确认：

- 下载是普通链接、预签名链接还是单独 API；
- 文件名来自 `Content-Disposition` 还是 JSON 字段；
- 下载请求是否要求一次性令牌；
- 每个下载结果是否仍能与原报验编号精确对应。

### 3. 没有稳定 API 时检查 HTML

使用 Playwright 为以下元素建立稳定定位：

- 查询输入框和提交按钮；
- 唯一结果卡片；
- 报验编号字段；
- 提交历史和最终状态；
- 附件下载链接。

优先使用可访问名称、`data-*` 属性和稳定 ID，不要依赖容易变化的第几个 `div`。

### 4. 实现适配器

复制 `PortalAdapter` 接口，新适配器每次只查询一条，并返回：

```json
{
  "match_code": "DEMO-GQC-IR-00001",
  "submissions": [
    {
      "label": "Issued For Inspection",
      "lifecycle": "Active",
      "updated_at": "2026-07-27T05:10:00Z"
    }
  ]
}
```

系统会继续负责：

- 核对 `match_code` 与请求编号完全一致；
- 排除 `Cancelled`；
- 把允许的门户文字映射为标准状态；
- 根据台账修订列生成变更建议；
- 不确定时失败关闭。

### 5. 配置和验证

秘密只放环境变量，例如：

```powershell
$env:ITR_PORTAL_TOKEN = "仅在本机设置"
python -m unittest discover -s tests -v
python scripts/run_pipeline.py --config config.example.json
python -m http.server 8000 --directory public
```

确认离线 fixture、错误编号、错配编号、取消提交和缺失修订列都经过测试后，再部署定时任务。真实写回应保持为独立的私有组件。

## 方法 B：交给 AI 完成适配

把下面提示词交给具备浏览器控制和代码编辑能力的 AI。网站地址、台账格式和字段名称由你填写，但不要在公开对话提供密码、Cookie 或 Token。

```text
请帮我把“报验单检测系统 / ITR-status”接入一个我有权访问的网站。

目标：从我的台账逐条读取报验编号，在网站查询最终有效状态，并生成 dashboard.json；第一阶段只读，不写回。

请执行：
1. 先运行现有测试并阅读 config.example.json、PortalAdapter 和状态规则。
2. 用浏览器开发者工具观察我手动查询一个测试编号的过程。
3. 优先从 Network 的 Fetch/XHR 识别查询 API、请求方法、参数、分页和下载接口；如果没有稳定 API，再使用 Playwright 分析 HTML。
4. 不要输出或提交密码、Cookie、Token、真实网址和真实工程数据；秘密只从环境变量读取。
5. 查询后必须核对 match_code 与请求编号完全一致，排除 Cancelled，只接受状态白名单；结果不确定时失败关闭。
6. 为新适配器增加离线 fixture 和单元测试，先做 preflight-only。
7. 给我列出需要自己填写的环境变量和配置项，并生成可运行命令。

网站入口：[填写授权网站地址]
台账格式：[JSON / CSV / Excel / Google Sheet]
查询编号字段：[填写列名]
允许下载附件：[是 / 否]
```

AI 完成后，仍应由你核对请求范围、输出编号、状态含义和是否产生任何写操作。
