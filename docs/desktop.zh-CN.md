# Windows 桌面版使用说明

桌面版把公开流水线包装成一个可下载的 Windows EXE。它适合本地导入台账、运行只读核查、查看错误与变更建议；不包含真实网站账号，也不会回写源台账。

## 下载与启动

1. 打开仓库的 **Actions → Build Windows desktop app**。
2. 下载构建产物 `ITR-status-Desktop-Windows-x64` 并解压。
3. 双击 `ITR-status-Desktop.exe`。
4. Windows SmartScreen 若提示“未知发布者”，请选择“更多信息 → 仍要运行”。当前开源构建未做商业代码签名。

## 最快体验

程序首次打开会自动载入合成样例。直接点击“开始核查”，完成后点击“打开仪表盘”。所有结果默认保存在：

```text
%USERPROFILE%\ITR-status Workspace\
├── dashboard\                 本地仪表盘
├── artifacts\
│   ├── run_summary.json       本次汇总
│   ├── proposed_writeback.json 只读变更建议
│   └── errors.json            未解决记录
└── .itr-status\last-run.json  本次本地配置
```

## 导入自己的台账

支持 JSON、CSV 与 XLSX。JSON 沿用仓库数据契约；CSV/XLSX 的推荐列如下：

| 列 | 必需 | 说明 |
|---|---:|---|
| `itr_id` 或 `IR Number` | 是 | 报验编号 |
| `task_id` | 否 | 缺失时自动生成 `ROW-xxxxx` |
| `site` / `Location` | 否 | 地点 |
| `process` / `Activity` | 否 | 工序 |
| `status` | 建议 | 台账当前状态 |
| `REV-00`, `REV-01`... | 建议 | 连续的修订状态列 |
| `track`, `chainage`, `submitted_date` | 否 | 展示字段 |

XLSX 默认读取当前活动工作表，也可在 UI 中明确填写工作表名称。程序不会修改所选 Excel/CSV/JSON。

## 两种查询来源

- **离线结果 JSON**：适合样例、测试和从已授权系统导出的脱敏结果。
- **私有 HTTP JSON 网关**：适合组织自行维护的授权查询服务。接口每次接收 `itr_id` 查询参数，并返回项目 README 中的 `match_code + submissions` 契约。

令牌只能通过环境变量传入。不要把 Token、Cookie、账号或真实项目数据提交到公开仓库。

## 编号规则

桌面版允许配置编号正则，以兼容不同组织的 IR 格式。规则必须包含命名组 `base`，可选命名组 `revision`：

```regex
^(?P<base>[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-IR-\d{5})(?:-(?P<revision>\d{2}))?$
```

编号不符合规则、网站返回编号不完全一致、状态冲突、修订列不连续时，该行会失败关闭并进入 `errors.json`。

## 从源码构建

在 Windows PowerShell 中运行：

```powershell
.\build_desktop.ps1
```

脚本会安装桌面依赖、运行测试，再生成：

```text
dist\ITR-status-Desktop.exe
```
