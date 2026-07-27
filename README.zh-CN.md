# 报验单检测系统 / ITR-status

[English](README.md) · [在线样例](https://weajpp.github.io/itr-status-dashboard-demo/) · [完整接入教程](docs/adaptation-guide.zh-CN.md)

这是一个隐私安全、可以直接运行的开源参考项目，首先用于**工程报验单（IR / ITR）的日常状态查询**，也可以用于其他需要定期查询状态的网站。

它不是单独部署一个网页，而是包含完整查询流程：

```text
源台账 → 运行前预检 → 编号校验 → 逐条查询网站
      → 返回编号精确匹配 → 状态与修订规则
      → 受保护的变更建议 → 中英文仪表盘
```

仓库中的人名、编号、地点和结果均为合成数据。公开样例不含生产网址、账号密码、Cookie、Token、表格 ID 或真实工程编号，并强制关闭写回。

## 两种接入真实网站的方法

### 方法 A：自己部署并分析 HTML / API

使用浏览器 Network 的 Fetch/XHR 观察一次人工查询，优先找出查询、分页和获授权下载的 API。没有稳定 API 时再用 Playwright 定位搜索框、唯一结果、最终状态和下载链接。实现 `PortalAdapter` 后，先运行离线测试和只读预检。

### 方法 B：让 AI 帮你适配

在线网页已经提供可复制的完整提示词。把授权网站地址、台账格式和编号列名补进去，交给具备浏览器和代码能力的 AI。AI 必须保持只读、隐藏秘密、精确核对编号，并为适配器添加 fixture 和测试。

具体 Network 检查、下载接口判断、HTML 定位方式、环境变量和完整提示词见[接入教程](docs/adaptation-guide.zh-CN.md)。

## 已实现的安全逻辑

- JSON 和 CSV 台账适配器；
- 离线门户 fixture 和可选 HTTP JSON 适配器；
- `pending` 等错误编号在查询前拒绝；
- 每次查询后精确核对 `match_code`；
- 排除已取消提交，最终状态必须属于白名单；
- `Issued For Inspection → UR`；
- `Ready for Sign Off/Out → READY`；
- 以台账的 `REV-00...REV-NN` 计算目标修订；
- 显式 `-20` 特殊编号保持不变；
- 单行不确定即失败关闭，不产生写回建议；
- 公开版本只生成建议产物，不修改源台账。

## 本地运行

只需要 Python 3.10+：

```bash
python -m unittest discover -s tests -v
python scripts/run_pipeline.py --config config.example.json
python -m http.server 8000 --directory public
```

打开 `http://localhost:8000`。页面首次打开默认为中文，右上角可以切换英文；测试时也可以使用 `?lang=zh` 或 `?lang=en`。

生成文件：

- `public/data/dashboard.json`：网页数据接口；
- `artifacts/run_summary.json`：运行汇总；
- `artifacts/proposed_writeback.json`：待审核的变更建议；
- `artifacts/errors.json`：未解决记录。

## 目录

```text
src/itr_pipeline/       流水线、适配器、规则和数据模型
scripts/run_pipeline.py 命令行入口
sample_data/            合成台账和门户返回结果
tests/                  安全规则与流程测试
public/                 中英文仪表盘和接入提示词
docs/                   架构与接入教程
.github/workflows/      测试、生成和部署
```

## 贡献者

- [WeaJpp](https://github.com/WeaJpp)：创建者与业务流程设计
- [OpenAI Codex](https://github.com/codex)：实现协作者

采用 MIT 许可证。
