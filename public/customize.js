Object.assign(TEXT.zh,{
 brand:"报验单检测系统 / ITR-status",adaptTitle:"把它接到你的网站",adaptIntro:"两种接入方法：自己分析网页，或者把标准提示词交给 AI。",
 readOnlyFirst:"先只读，后写回",flowLedger:"准备台账",flowInspect:"识别 HTML / API",flowAdapter:"编写适配器",flowVerify:"精确匹配与测试",flowDeploy:"部署定时查询",
 selfTitle:"自己部署并分析网站",selfDesc:"适合懂浏览器开发者工具、HTTP 或 Playwright 的用户。",
 self1:"获得网站授权，用测试编号手动查询一次。",self2:"在 Network 的 Fetch/XHR 中找查询请求、下载接口和 JSON 返回值。",
 self3:"没有 API 时，检查搜索框、结果卡片和下载链接的 HTML 选择器。",self4:"实现 PortalAdapter，只返回 match_code 与 submissions。",
 self5:"把 Token 放环境变量，先跑测试与只读预检，再部署定时任务。",openGuide:"打开完整接入教程 ↗",
 aiTitle:"把提示词交给 AI",aiDesc:"让具备浏览器和代码能力的 AI 帮你定位接口并生成适配器。",
 copyPrompt:"复制提示词",copied:"已复制",promptWarning:"不要把密码、Cookie 或生产数据粘贴进公开对话。"
});
Object.assign(TEXT.en,{
 brand:"ITR-status · Inspection Checker",adaptTitle:"Connect it to your website",adaptIntro:"Choose either a hands-on inspection or a ready-to-use AI prompt.",
 readOnlyFirst:"Read first, write later",flowLedger:"Prepare ledger",flowInspect:"Find HTML / API",flowAdapter:"Build adapter",flowVerify:"Match and test",flowDeploy:"Schedule deployment",
 selfTitle:"Deploy and inspect it yourself",selfDesc:"For users familiar with browser DevTools, HTTP, or Playwright.",
 self1:"Get authorization and run one manual query with a test identity.",self2:"Use Network → Fetch/XHR to identify query, download, and JSON endpoints.",
 self3:"If there is no API, inspect selectors for the search box, result card, and download link.",self4:"Implement PortalAdapter and return only match_code and submissions.",
 self5:"Keep tokens in environment variables; run tests and read-only preflight before scheduling.",openGuide:"Open the complete guide ↗",
 aiTitle:"Give the task to an AI",aiDesc:"Let a browser-and-code capable AI identify the interface and generate an adapter.",
 copyPrompt:"Copy prompt",copied:"Copied",promptWarning:"Never paste passwords, cookies, or production data into a public conversation."
});
const PROMPTS={
zh:`请帮我把“报验单检测系统 / ITR-status”接入一个我有权访问的网站。

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
允许下载附件：[是 / 否]`,
en:`Help me connect “ITR-status · Inspection Checker” to a website I am authorized to access.

Goal: read inspection identities from my ledger, query the final active status, and generate dashboard.json. Phase one must be read-only.

1. Run the existing tests and inspect config.example.json, PortalAdapter, and status rules.
2. Observe one manual test query with browser DevTools.
3. Prefer Network Fetch/XHR for query, pagination, and download endpoints; use Playwright HTML selectors only when no stable API exists.
4. Never print or commit passwords, cookies, tokens, private URLs, or production records. Read secrets only from environment variables.
5. Require an exact match_code, discard Cancelled lifecycle entries, allowlist statuses, and fail closed on uncertainty.
6. Add offline fixtures, focused tests, and a preflight-only mode.
7. List the environment variables and configuration I must provide, then give runnable commands.

Authorized site: [URL]
Ledger: [JSON / CSV / Excel / Google Sheet]
Identity column: [name]
Attachment download allowed: [yes / no]`
};
function updatePrompt(){
 document.title=state.lang==="zh"?"报验单检测系统 / ITR-status":"ITR-status · Inspection Checker";
 document.querySelector("#aiPrompt").textContent=PROMPTS[state.lang];
}
const originalApplyLanguage=applyLanguage;
applyLanguage=function(){originalApplyLanguage();updatePrompt();};
document.querySelector("#copyPrompt").addEventListener("click",async event=>{
 try{
  await navigator.clipboard.writeText(PROMPTS[state.lang]);
  event.currentTarget.textContent=TEXT[state.lang].copied;
  setTimeout(()=>event.currentTarget.textContent=TEXT[state.lang].copyPrompt,1400);
 }catch{
  document.querySelector("#aiPrompt").focus();
 }
});
applyLanguage();
