const SAMPLE_ITRS = [
  { site: "Demo North", process: "Bottom Ballast", ir: "DEMO-GQC-IR-00001", status: "CODE-1", track: "Left", chainage: "0+000–0+500", updated: "2026-01-15" },
  { site: "Demo North", process: "Track Laying", ir: "DEMO-GQC-IR-00002", status: "CODE-2", track: "Left", chainage: "0+500–1+000", updated: "2026-01-14" },
  { site: "Demo North", process: "1st Tamping", ir: "DEMO-GQC-IR-00003", status: "UR", track: "Right", chainage: "1+000–1+500", updated: "2026-01-13" },
  { site: "Demo North", process: "MFBW", ir: "DEMO-GQC-IR-00004", status: "CODE-1", track: "Right", chainage: "1+500–2+000", updated: "2026-01-12" },
  { site: "Demo North", process: "Destressing", ir: "DEMO-GQC-IR-00005", status: "CODE-5", track: "Left", chainage: "2+000–2+500", updated: "2026-01-11" },
  { site: "Demo South", process: "Bottom Ballast", ir: "DEMO-GQC-IR-00006", status: "CODE-2", track: "Right", chainage: "10+000–10+500", updated: "2026-01-15" },
  { site: "Demo South", process: "Track Laying", ir: "DEMO-GQC-IR-00007", status: "CODE-1", track: "Right", chainage: "10+500–11+000", updated: "2026-01-14" },
  { site: "Demo South", process: "Final Tamping", ir: "DEMO-GQC-IR-00008", status: "CODE-4", track: "Left", chainage: "11+000–11+500", updated: "2026-01-13" },
  { site: "Demo South", process: "Turnout Installation", ir: "DEMO-GQC-IR-00009", status: "UR", track: "N/A", chainage: "11+750", updated: "2026-01-12" },
  { site: "Demo South", process: "UT", ir: "DEMO-GQC-IR-00010", status: "DRAFT", track: "N/A", chainage: "12+000", updated: "2026-01-10" },
  { site: "Demo Depot", process: "Turnout Installation", ir: "DEMO-GQC-IR-00011", status: "CODE-1", track: "N/A", chainage: "Yard A", updated: "2026-01-15" },
  { site: "Demo Depot", process: "Aluminothermic Welding", ir: "DEMO-GQC-IR-00012", status: "CODE-2", track: "N/A", chainage: "Yard B", updated: "2026-01-14" },
  { site: "Demo Depot", process: "Fouling Point", ir: "DEMO-GQC-IR-00013", status: "CODE-5", track: "N/A", chainage: "Turnout 01", updated: "2026-01-13" },
  { site: "Demo Depot", process: "Datum Plate", ir: "DEMO-GQC-IR-00014", status: "CODE-1", track: "N/A", chainage: "Turnout 02", updated: "2026-01-12" }
];

const STATUS_ORDER = ["CODE-1", "CODE-2", "CODE-4", "CODE-5", "UR", "DRAFT"];
const STATUS_COLORS = {
  "CODE-1": "#278466",
  "CODE-2": "#c48826",
  "CODE-4": "#b85952",
  "CODE-5": "#3e76a8",
  "UR": "#7861a8",
  "DRAFT": "#76808a"
};

const els = {
  kpis: document.querySelector("#kpis"),
  siteGrid: document.querySelector("#siteGrid"),
  rows: document.querySelector("#itrRows"),
  search: document.querySelector("#searchInput"),
  site: document.querySelector("#siteFilter"),
  status: document.querySelector("#statusFilter"),
  reset: document.querySelector("#resetFilters"),
  export: document.querySelector("#exportCsv"),
  theme: document.querySelector("#themeToggle"),
  visibleCount: document.querySelector("#visibleCount"),
  empty: document.querySelector("#emptyState")
};

const countBy = (items, key) => items.reduce((acc, item) => {
  acc[item[key]] = (acc[item[key]] || 0) + 1;
  return acc;
}, {});

function fillFilters() {
  [...new Set(SAMPLE_ITRS.map(row => row.site))].sort().forEach(site => {
    els.site.add(new Option(site, site));
  });
  STATUS_ORDER.forEach(status => els.status.add(new Option(status, status)));
}

function renderKpis(items) {
  const counts = countBy(items, "status");
  const cards = [
    ["Total ITR", items.length, "#b58a42"],
    ...STATUS_ORDER.map(status => [status, counts[status] || 0, STATUS_COLORS[status]])
  ];
  els.kpis.innerHTML = cards.map(([label, value, color]) => `
    <article class="kpi" style="--accent:${color}">
      <span class="kpi-label">${label}</span>
      <strong class="kpi-value">${value}</strong>
      <div class="kpi-line"></div>
    </article>
  `).join("");
}

function renderSites(items) {
  const sites = [...new Set(items.map(row => row.site))].sort();
  els.siteGrid.innerHTML = sites.map(site => {
    const siteRows = items.filter(row => row.site === site);
    const counts = countBy(siteRows, "status");
    const bars = STATUS_ORDER
      .filter(status => counts[status])
      .map(status => `<span title="${status}: ${counts[status]}" style="width:${counts[status] / siteRows.length * 100}%;background:${STATUS_COLORS[status]}"></span>`)
      .join("");
    const legend = STATUS_ORDER
      .filter(status => counts[status])
      .map(status => `
        <div class="legend-item" style="--accent:${STATUS_COLORS[status]}">
          <span class="legend-label"><span class="dot"></span>${status}</span>
          <strong>${counts[status]}</strong>
        </div>
      `).join("");
    return `
      <article class="site-card">
        <div class="site-card-head"><span class="site-name">${site}</span><span class="site-total">${siteRows.length} ITR</span></div>
        <div class="status-bar">${bars}</div>
        <div class="site-legend">${legend}</div>
      </article>
    `;
  }).join("");
  if (!sites.length) els.siteGrid.innerHTML = `<div class="empty">当前筛选没有站点数据。</div>`;
}

function renderRows(items) {
  els.rows.innerHTML = items.map(row => `
    <tr>
      <td>${row.site}</td>
      <td>${row.process}</td>
      <td><span class="ir-code">${row.ir}</span></td>
      <td><span class="pill" style="--accent:${STATUS_COLORS[row.status]}">${row.status}</span></td>
      <td>${row.track}</td>
      <td>${row.chainage}</td>
      <td>${row.updated}</td>
    </tr>
  `).join("");
  els.empty.hidden = items.length !== 0;
  els.visibleCount.textContent = `显示 ${items.length} / ${SAMPLE_ITRS.length} 条模拟记录`;
}

function filteredRows() {
  const query = els.search.value.trim().toLowerCase();
  return SAMPLE_ITRS.filter(row => {
    const haystack = Object.values(row).join(" ").toLowerCase();
    return (!query || haystack.includes(query))
      && (!els.site.value || row.site === els.site.value)
      && (!els.status.value || row.status === els.status.value);
  });
}

function update() {
  const rows = filteredRows();
  renderKpis(rows);
  renderSites(rows);
  renderRows(rows);
}

function exportCsv() {
  const fields = ["site", "process", "ir", "status", "track", "chainage", "updated"];
  const quote = value => `"${String(value).replaceAll('"', '""')}"`;
  const csv = [fields.join(","), ...filteredRows().map(row => fields.map(field => quote(row[field])).join(","))].join("\n");
  const blob = new Blob([`\ufeff${csv}`], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "itr-demo-filtered.csv";
  link.click();
  URL.revokeObjectURL(url);
}

[els.search, els.site, els.status].forEach(el => el.addEventListener("input", update));
els.reset.addEventListener("click", () => {
  els.search.value = "";
  els.site.value = "";
  els.status.value = "";
  update();
});
els.export.addEventListener("click", exportCsv);
els.theme.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem("itr-demo-theme", document.body.classList.contains("dark") ? "dark" : "light");
});

if (localStorage.getItem("itr-demo-theme") === "dark") document.body.classList.add("dark");
fillFilters();
update();

