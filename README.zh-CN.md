# ITR 状态查询仪表盘

[English](README.md) · [在线样例](https://weajpp.github.io/itr-status-dashboard-demo/)

这是一个隐私安全、可以直接运行的开源参考项目，首先用于**工程报验单（IR / ITR）的日常状态查询**，也可以通过适配器用于其他需要定期查询状态的网站。

这个仓库不再只是一个网页，而是包含从源台账到查询证据的完整安全流程：

```text
源台账 → 运行前预检 → 编号校验 → 逐条顺序查询
      → 返回编号精确匹配 → 状态与修订规则
      → 受保护的变更建议 → 中英文仪表盘
```

仓库中的人名、编号、地点和查询结果全部是合成数据，不含生产网址、账号密码、Cookie、Token、表格 ID 或真实工程编号。公开样例会强制关闭写回。

## 已实现的具体流程

- JSON 和 CSV 台账读取适配器
- 用于 CI 和 GitHub Pages 的离线门户模拟器
- 可连接私有脱敏接口的 HTTP JSON 适配器契约
- 在查询前拒绝 `pending` 等错误编号
- 每次查询后精确核对 `match_code`
- 排除已取消的提交，并对最终状态执行白名单校验
- 精确映射：`Issued For Inspection → UR`，`Ready for Sign Off/Out → READY`
- 以台账中的 `REV-00`、`REV-01` 为准计算目标修订
- 显式 `-20` 特殊编号保持不变
- 单行异常立即关闭该行，不产生写回建议
- 公开版只生成建议产物，不改源台账
- 浏览器中文环境显示全中文，英文环境显示全英文，并支持手动切换
- 单元测试、每日定时生成和 GitHub Pages 部署

## 本地运行

只需要 Python 3.10+，流水线本身没有第三方依赖。

```bash
python -m unittest discover -s tests -v
python scripts/run_pipeline.py --config config.example.json
python -m http.server 8000 --directory public
```

打开 `http://localhost:8000`。测试时可用 `?lang=zh` 或 `?lang=en` 强制指定语言。

生成的文件：

- `public/data/dashboard.json`：网页数据接口
- `artifacts/run_summary.json`：本次运行汇总
- `artifacts/proposed_writeback.json`：待人工审核的变更建议
- `artifacts/errors.json`：未解决记录

## 接入真实系统

为权威工作簿或数据库实现 `SourceAdapter`，再为获得授权的网站或内部 API 实现 `PortalAdapter`。门户返回数据的最小契约如下：

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

真实地址、选择器和认证信息应只保存在私有部署环境。公开配置拒绝 `writeback.enabled=true`；生产写回应放在单独审核的适配器中，并配套备份、范围检查和审计日志。

更多内容见[架构说明](docs/architecture.zh-CN.md)、[参与贡献](CONTRIBUTING.md)和[安全说明](SECURITY.md)。

## 目录结构

```text
src/itr_pipeline/       流水线、适配器、规则和数据模型
scripts/run_pipeline.py 命令行入口
sample_data/            合成台账和门户返回结果
tests/                  安全规则与流程测试
public/                 自动选择语言的仪表盘
.github/workflows/      测试、生成和部署
```

## 贡献者

- [WeaJpp](https://github.com/WeaJpp)：创建者与业务流程设计
- [OpenAI Codex](https://github.com/codex)：实现协作者

采用 MIT 许可证。
