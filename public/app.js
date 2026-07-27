const TEXT={en:{
brand:"ITR Status Pipeline",source:"Source",eyebrow:"OPEN-SOURCE WORKFLOW DEMO",title:"Inspection status, from ledger to evidence.",subtitle:"A runnable daily workflow for engineering inspection requests—and any website that needs routine status checks.",lastRun:"Latest pipeline run",privacy:"Synthetic data only. No credentials, private URLs, cookies, or production identifiers.",pipeline:"Daily query pipeline",writebackOff:"Writeback disabled",distribution:"Status distribution",changes:"Guarded change proposals",records:"Inspection register",export:"Export CSV",search:"Search by ID, site, process, or chainage",empty:"No matching records.",exceptions:"Fail-closed exceptions",footer:"Built for engineering inspection requests; adaptable to other daily website checks.",success:"Success",warning:"Needs review",all:"All statuses",sourceRows:"Source rows",scanned:"Queried",proposals:"Proposals",unresolved:"Unresolved",ur:"Confirmed UR",scope:"Scope complete",yes:"Yes",no:"No",task:"Task",itr:"ITR identity",from:"Ledger",to:"Observed",revision:"Target revision",identity:"Proposed identity",site:"Site",process:"Process",track:"Track",chainage:"Chainage",status:"Status",state:"Query state",updated:"Updated",phase:{preflight:"Preflight",source:"Source",identity:"Identity",crawl:"Crawl",rules:"Rules",writeback:"Writeback",publish:"Publish"}},
zh:{brand:"ITR 状态查询流水线",source:"源码",eyebrow:"开源工作流样例",title:"从工程台账，到可追溯的状态证据。",subtitle:"一套可运行的工程报验单日常查询流程，也可适配其他需要定期查询状态的网站。",lastRun:"最近一次流水线运行",privacy:"仅使用合成数据，不含账号密码、私有网址、Cookie 或真实工程编号。",pipeline:"日常状态查询流水线",writebackOff:"已禁用写回",distribution:"状态分布",changes:"受保护的变更建议",records:"工程报验台账",export:"导出 CSV",search:"按编号、地点、工序或里程搜索",empty:"没有符合条件的记录。",exceptions:"失败即关闭的异常项",footer:"为工程报验单而做，也可用于其他网站的日常状态查询。",success:"成功",warning:"需要复核",all:"全部状态",sourceRows:"台账总数",scanned:"已查询",proposals:"变更建议",unresolved:"未解决",ur:"确认仍为 UR",scope:"范围完整",yes:"是",no:"否",task:"任务",itr:"报验编号",from:"台账状态",to:"查询状态",revision:"目标修订",identity:"建议编号",site:"地点",process:"工序",track:"线路",chainage:"里程",status:"状态",state:"查询结果",updated:"更新时间",phase:{preflight:"预检",source:"读取台账",identity:"编号校验",crawl:"顺序查询",rules:"规则判断",writeback:"写回",publish:"发布"}}};
const VALUE_ZH={"Right Track":"右线","Left Track":"左线","Both Tracks":"双线","Siding 1":"侧线 1","Siding 2":"侧线 2","Turnout 101":"道岔 101","Reception Line":"接车线","resolved":"已确认","not_scanned":"未查询","skipped_by_policy":"按规则跳过","rejected_before_query":"查询前拒绝","error":"查询异常"};
const state={data:null,lang:null,query:"",status:"ALL"},$=s=>document.querySelector(s);
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
const requested=new URLSearchParams(location.search).get("lang");
state.lang=["zh","en"].includes(requested)?requested:(localStorage.getItem("itr-lang")||(navigator.language.toLowerCase().startsWith("zh")?"zh":"en"));
const t=k=>k.split(".").reduce((v,p)=>v?.[p],TEXT[state.lang])??k;
const local=(item,key)=>state.lang==="zh"?(item[`${key}_zh`]||item[key]):item[key];
const value=v=>state.lang==="zh"?(VALUE_ZH[v]||v):v;
const badge=v=>`<span class="status ${esc(v)}">${esc(v||"—")}</span>`;

function applyLanguage(){
 document.documentElement.lang=state.lang==="zh"?"zh-CN":"en";
 document.title=state.lang==="zh"?"ITR 状态查询仪表盘":"ITR Status Dashboard";
 document.querySelectorAll("[data-i18n]").forEach(el=>el.textContent=t(el.dataset.i18n));
 document.querySelectorAll("[data-i18n-placeholder]").forEach(el=>el.placeholder=t(el.dataset.i18nPlaceholder));
 $("#language").textContent=state.lang==="zh"?"EN":"中文";
 if(state.data)render();
}
function render(){
 const d=state.data,s=d.summary;
 $("#runStatus").textContent=s.unresolved?t("warning"):t("success");
 $("#runTime").textContent=new Intl.DateTimeFormat(state.lang==="zh"?"zh-CN":"en-GB",{dateStyle:"medium",timeStyle:"short"}).format(new Date(d.generated_at));
 const metrics=[["sourceRows",s.source_rows],["scanned",s.scanned],["proposals",s.changes],["unresolved",s.unresolved],["ur",s.confirmed_still_ur],["scope",s.scope_complete?t("yes"):t("no")]];
 $("#metrics").innerHTML=metrics.map(([k,v])=>`<div class="metric"><strong>${esc(v)}</strong><span>${t(k)}</span></div>`).join("");
 $("#pipeline").innerHTML=d.phases.map(p=>`<div class="step ${p.status}"><b>${t(`phase.${p.key}`)}</b><p>${esc(state.lang==="zh"?p.detail_zh:p.detail_en)}</p></div>`).join("");
 const total=Object.values(s.status_counts).reduce((a,b)=>a+b,0)||1;
 $("#distribution").innerHTML=Object.entries(s.status_counts).map(([k,v])=>`<div class="bar-row"><div class="bar-label"><span>${badge(k)}</span><b>${v}</b></div><div class="bar"><i style="width:${v/total*100}%"></i></div></div>`).join("");
 $("#changeCount").textContent=s.changes;
 $("#changeHead").innerHTML=`<tr>${["task","itr","from","to","revision","identity"].map(k=>`<th>${t(k)}</th>`).join("")}</tr>`;
 $("#changeBody").innerHTML=d.changes.map(x=>`<tr><td>${esc(x.task_id)}</td><td>${esc(x.itr_id)}</td><td>${badge(x.current_status)}</td><td>${badge(x.observed_status)}</td><td>${esc(x.target_revision)}</td><td>${esc(x.identity_after_write)}</td></tr>`).join("");
 renderRecords();
 $("#errors").innerHTML=d.errors.length?d.errors.map(x=>`<div class="error-item"><b>${esc(x.itr_id)}<br>${esc(x.code)}</b><p>${esc(state.lang==="zh"?x.message_zh:x.message_en)}</p></div>`).join(""):`<div class="empty">${t("empty")}</div>`;
}
function renderRecords(){
 const rows=state.data.records.filter(r=>[r.itr_id,local(r,"site"),local(r,"process"),value(r.track),r.chainage].join(" ").toLowerCase().includes(state.query.toLowerCase())&&(state.status==="ALL"||r.display_status===state.status));
 $("#recordHead").innerHTML=`<tr>${["itr","site","process","track","chainage","status","state","updated"].map(k=>`<th>${t(k)}</th>`).join("")}</tr>`;
 $("#recordBody").innerHTML=rows.map(r=>`<tr><td>${esc(r.itr_id)}</td><td>${esc(local(r,"site"))}</td><td>${esc(local(r,"process"))}</td><td>${esc(value(r.track))}</td><td>${esc(r.chainage)}</td><td>${badge(r.display_status)}</td><td>${esc(value(r.query_state))}</td><td>${esc(r.updated_at)}</td></tr>`).join("");
 $("#empty").hidden=rows.length>0;
 const current=$("#statusFilter").value||state.status,statuses=[...new Set(state.data.records.map(r=>r.display_status))].sort();
 $("#statusFilter").innerHTML=`<option value="ALL">${t("all")}</option>`+statuses.map(x=>`<option>${esc(x)}</option>`).join("");
 $("#statusFilter").value=current;
}
$("#language").addEventListener("click",()=>{state.lang=state.lang==="zh"?"en":"zh";localStorage.setItem("itr-lang",state.lang);applyLanguage()});
$("#theme").addEventListener("click",()=>{const dark=document.documentElement.dataset.theme==="dark";document.documentElement.dataset.theme=dark?"light":"dark";localStorage.setItem("itr-theme",dark?"light":"dark")});
$("#search").addEventListener("input",e=>{state.query=e.target.value;renderRecords()});
$("#statusFilter").addEventListener("change",e=>{state.status=e.target.value;renderRecords()});
$("#export").addEventListener("click",()=>{
 const header=["itr","site","process","track","chainage","status","state","updated"].map(t),quote=v=>`"${String(v??"").replaceAll('"','""')}"`;
 const lines=[header.map(quote).join(","),...state.data.records.map(r=>[r.itr_id,local(r,"site"),local(r,"process"),value(r.track),r.chainage,r.display_status,value(r.query_state),r.updated_at].map(quote).join(","))];
 const a=document.createElement("a");a.href=URL.createObjectURL(new Blob(["\ufeff"+lines.join("\n")],{type:"text/csv"}));a.download=`itr-demo-${state.lang}.csv`;a.click();URL.revokeObjectURL(a.href);
});
document.documentElement.dataset.theme=localStorage.getItem("itr-theme")||"light";
applyLanguage();
fetch("data/dashboard.json").then(r=>{if(!r.ok)throw new Error(r.status);return r.json()}).then(d=>{state.data=d;render()}).catch(()=>{$("main").innerHTML=`<p>${state.lang==="zh"?"仪表盘数据无法读取。":"Dashboard data unavailable."}</p>`});
