const pptxgen = require("pptxgenjs");
const fs = require("fs");

const S = JSON.parse(fs.readFileSync("synthesis.json", "utf8"));
const NAVY = "1E2761";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const INK = "1A1A2E";
const MUTED = "64748B";
const RED = "D64545";
const AMBER = "E8A33D";
const GREEN = "3FA34D";
const RAG_COLOR = { Red: RED, Amber: AMBER, Green: GREEN };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Project Health Reporting Agent";
pres.title = "Monthly Project Health Review";

const W = 13.3, H = 7.5;

function ragDot(slide, x, y, color, d = 0.22) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: RAG_COLOR[color] || color }, line: { type: "none" } });
}

function pageNum(slide, n) {
  slide.addText(`${n}`, { x: W - 0.7, y: H - 0.5, w: 0.5, h: 0.3, fontSize: 10, color: MUTED, align: "right" });
}

function footer(slide, n) {
  slide.addText("Project Health Reporting Agent — Monthly Executive Synthesis", { x: 0.5, y: H - 0.5, w: 6, h: 0.3, fontSize: 9, color: MUTED });
  pageNum(slide, n);
}

{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  ragDot(s, 0.9, 0.9, "Red", 0.16);
  ragDot(s, 1.2, 0.9, "Amber", 0.16);
  ragDot(s, 1.5, 0.9, "Green", 0.16);
  s.addText("Monthly Project Health Review", { x: 0.9, y: 2.5, w: 11, h: 1.1, fontSize: 40, bold: true, color: WHITE, fontFace: "Cambria" });
  s.addText("Professional Services Portfolio — S2P Implementation Program", { x: 0.9, y: 3.6, w: 11, h: 0.6, fontSize: 20, color: ICE, fontFace: "Calibri" });
  s.addText(`${S.n_projects} active implementations reviewed  •  Generated ${new Date(S.generated_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}`,
    { x: 0.9, y: 6.5, w: 11, h: 0.4, fontSize: 13, color: ICE, italic: true });
}

{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("Portfolio Snapshot", { x: 0.6, y: 0.4, w: 8, h: 0.7, fontSize: 30, bold: true, color: INK, fontFace: "Cambria" });
  s.addText("Where the portfolio stands today, at a glance.", { x: 0.6, y: 1.05, w: 8, h: 0.4, fontSize: 14, color: MUTED });

  const dist = S.rag_distribution;
  const chartData = [{ name: "Projects", labels: ["Red", "Amber", "Green"], values: [dist.Red, dist.Amber, dist.Green] }];
  s.addChart(pres.charts.DOUGHNUT, chartData, {
    x: 0.6, y: 1.6, w: 4.6, h: 4.6,
    chartColors: [RED, AMBER, GREEN],
    showLegend: true, legendPos: "b", legendColor: INK, legendFontSize: 12,
    showPercent: false, showValue: true, dataLabelColor: WHITE, dataLabelFontSize: 13,
    showTitle: false,
  });

  const statX = 5.7;
  s.addText(`${S.n_projects}`, { x: statX, y: 1.7, w: 3.2, h: 1.0, fontSize: 56, bold: true, color: NAVY, fontFace: "Cambria" });
  s.addText("active implementations", { x: statX, y: 2.6, w: 3.2, h: 0.4, fontSize: 13, color: MUTED });

  s.addText(`${Math.round(S.avg_pct_complete * 100)}%`, { x: statX, y: 3.3, w: 3.2, h: 1.0, fontSize: 56, bold: true, color: NAVY, fontFace: "Cambria" });
  s.addText("average completion across portfolio", { x: statX, y: 4.2, w: 3.2, h: 0.4, fontSize: 13, color: MUTED });

  s.addText(`${dist.Red}`, { x: statX, y: 4.9, w: 3.2, h: 1.0, fontSize: 56, bold: true, color: RED, fontFace: "Cambria" });
  s.addText("of the portfolio is currently RED", { x: statX, y: 5.8, w: 3.2, h: 0.4, fontSize: 13, color: MUTED });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 1.6, w: 3.4, h: 4.6, fill: { color: "F4F6FB" }, line: { type: "none" }, rectRadius: 0.08 });
  s.addText("Headline", { x: 9.65, y: 1.85, w: 2.8, h: 0.35, fontSize: 12, bold: true, color: NAVY });
  s.addText(
    `${dist.Red} of ${S.n_projects} implementation${S.n_projects === 1 ? "" : "s"} in the current sample ${S.n_projects > 1 ? "are" : "is"} flagged RED, with completion averaging ${Math.round(S.avg_pct_complete * 100)}%. Risk is not isolated to one workstream — it repeats across projects (see next slide).`,
    { x: 9.65, y: 2.25, w: 2.8, h: 3.8, fontSize: 13, color: INK, valign: "top" }
  );
  footer(s, 2);
}

{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("Cross-Project Trend Analysis", { x: 0.6, y: 0.4, w: 10, h: 0.7, fontSize: 30, bold: true, color: INK, fontFace: "Cambria" });
  s.addText("Recurring risk themes across the portfolio — not a per-project recap.", { x: 0.6, y: 1.05, w: 10, h: 0.4, fontSize: 14, color: MUTED });

  const themes = S.all_themes_ranked.slice(0, 6);
  s.addChart(pres.charts.BAR, [{
    name: "Occurrences", labels: themes.map(t => t.theme), values: themes.map(t => t.count),
  }], {
    x: 0.6, y: 1.7, w: 7.6, h: 4.9, barDir: "bar",
    chartColors: [NAVY],
    chartArea: { fill: { color: WHITE } },
    catAxisLabelColor: INK, valAxisLabelColor: MUTED, catAxisLabelFontSize: 12,
    valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK,
    showLegend: false,
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.5, y: 1.7, w: 4.2, h: 4.9, fill: { color: "F4F6FB" }, line: { type: "none" }, rectRadius: 0.08 });
  s.addText("Top recurring theme", { x: 8.85, y: 1.95, w: 3.5, h: 0.35, fontSize: 12, bold: true, color: NAVY });
  const top = S.recurring_themes[0];
  if (top) {
    s.addText(top.theme, { x: 8.85, y: 2.3, w: 3.5, h: 0.5, fontSize: 20, bold: true, color: INK, fontFace: "Cambria" });
    s.addText(`Flagged ${top.count} times across the portfolio.`, { x: 8.85, y: 2.85, w: 3.5, h: 0.4, fontSize: 12, color: MUTED });
    const exText = top.examples.map(e => ({ text: e, options: { bullet: true, breakLine: true, fontSize: 11, color: INK } }));
    s.addText(exText.length ? exText : [{ text: "See project detail.", options: { fontSize: 11, color: MUTED } }], { x: 8.85, y: 3.4, w: 3.5, h: 3.0, valign: "top" });
  }
  footer(s, 3);
}

{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("Emerging Risks", { x: 0.6, y: 0.4, w: 10, h: 0.7, fontSize: 30, bold: true, color: INK, fontFace: "Cambria" });
  s.addText("Where the portfolio is most exposed heading into next month.", { x: 0.6, y: 1.05, w: 10, h: 0.4, fontSize: 14, color: MUTED });

  const risks = S.recurring_themes.slice(0, 4);
  const colW = 5.9, gap = 0.4, startX = 0.6, startY = 1.75, rowH = 2.5;
  risks.forEach((r, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = startX + col * (colW + gap), y = startY + row * (rowH + 0.3);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: colW, h: rowH, fill: { color: "F4F6FB" }, line: { type: "none" }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 5, offset: 1.5, angle: 90, opacity: 0.08 } });
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.3, w: 0.45, h: 0.45, fill: { color: NAVY }, line: { type: "none" } });
    s.addText(`${r.count}x`, { x: x + 0.3, y: y + 0.3, w: 0.45, h: 0.45, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(r.theme, { x: x + 0.95, y: y + 0.28, w: colW - 1.2, h: 0.5, fontSize: 16, bold: true, color: INK, fontFace: "Cambria" });
    const exText = r.examples.slice(0, 3).map(e => ({ text: e, options: { bullet: true, breakLine: true, fontSize: 11.5, color: MUTED } }));
    s.addText(exText.length ? exText : [{ text: "Recurs across multiple phases.", options: { fontSize: 11.5, color: MUTED } }], { x: x + 0.3, y: y + 0.95, w: colW - 0.6, h: rowH - 1.2, valign: "top" });
  });
  footer(s, 4);
}

{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("Project-by-Project Comparison", { x: 0.6, y: 0.4, w: 10, h: 0.7, fontSize: 30, bold: true, color: INK, fontFace: "Cambria" });
  s.addText("Individual status, for reference alongside the portfolio-level trends above.", { x: 0.6, y: 1.05, w: 10, h: 0.4, fontSize: 14, color: MUTED });

  const header = [
    { text: "Project", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
    { text: "RAG", options: { bold: true, color: WHITE, fill: { color: NAVY }, align: "center" } },
    { text: "% Complete", options: { bold: true, color: WHITE, fill: { color: NAVY }, align: "center" } },
    { text: "Red Phases", options: { bold: true, color: WHITE, fill: { color: NAVY }, align: "center" } },
    { text: "Top Risk", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
  ];
  const rows = S.projects.map(p => [
    { text: p.name.replace("Zycus - ", ""), options: { color: INK, fontSize: 12 } },
    { text: p.rag, options: { color: RAG_COLOR[p.rag], bold: true, align: "center", fontSize: 12 } },
    { text: `${Math.round((p.pct_complete || 0) * 100)}%`, options: { color: INK, align: "center", fontSize: 12 } },
    { text: `${p.red_phase_count}`, options: { color: INK, align: "center", fontSize: 12 } },
    { text: p.top_risk.length > 90 ? p.top_risk.slice(0, 87) + "..." : p.top_risk, options: { color: MUTED, fontSize: 10.5 } },
  ]);

  s.addTable([header, ...rows], {
    x: 0.6, y: 1.75, w: 12.1, colW: [3.6, 1.1, 1.4, 1.3, 4.7],
    border: { pt: 0.5, color: "E2E8F0" }, autoPage: false,
    fontFace: "Calibri", valign: "middle", rowH: 0.6,
  });
  footer(s, 5);
}

{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("Executive Recommendations", { x: 0.6, y: 0.4, w: 10, h: 0.7, fontSize: 30, bold: true, color: INK, fontFace: "Cambria" });
  s.addText("Prioritized actions for the coming month.", { x: 0.6, y: 1.05, w: 10, h: 0.4, fontSize: 14, color: MUTED });

  const recs = [
    { n: "1", t: "Stabilize Training & Documentation workstreams", d: "The two most recurring risk themes this month. Assign a dedicated reviewer to clear sign-off backlogs before they cascade into UAT and Go-Live." },
    { n: "2", t: "Pool integration specialists across projects", d: "Supplier/Integration issues appear on multiple engagements simultaneously — a shared specialist pool reduces the chance the same bottleneck recurs project-to-project." },
    { n: "3", t: "Tighten baseline re-planning discipline", d: "Variance of 20-30+ days behind baseline was observed on critical-path tasks. Re-baseline formally rather than letting slippage compound silently." },
  ];
  let y = 1.85;
  recs.forEach(r => {
    s.addShape(pres.shapes.OVAL, { x: 0.6, y, w: 0.55, h: 0.55, fill: { color: NAVY }, line: { type: "none" } });
    s.addText(r.n, { x: 0.6, y, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(r.t, { x: 1.4, y: y - 0.05, w: 11.2, h: 0.45, fontSize: 17, bold: true, color: INK, fontFace: "Cambria" });
    s.addText(r.d, { x: 1.4, y: y + 0.4, w: 11.2, h: 0.6, fontSize: 13, color: MUTED });
    y += 1.55;
  });
  footer(s, 6);
}

{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Cadence & Next Steps", { x: 0.9, y: 0.6, w: 11, h: 0.7, fontSize: 30, bold: true, color: WHITE, fontFace: "Cambria" });

  const steps = [
    { t: "Weekly", d: "Agent runs against each live project plan, producing a RAG status with plain-English reasoning." },
    { t: "Monthly", d: "Weekly outputs are synthesized into this executive view — trends, not just recaps." },
    { t: "Ongoing", d: "PMs act on flagged Red/Amber items; next cycle measures whether the trend improved." },
  ];
  const colW = 3.7, gap = 0.4, startX = 0.9;
  steps.forEach((st, i) => {
    const x = startX + i * (colW + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.8, w: colW, h: 3.2, fill: { color: "273869" }, line: { type: "none" }, rectRadius: 0.08 });
    s.addText(st.t, { x: x + 0.3, y: 2.05, w: colW - 0.6, h: 0.5, fontSize: 18, bold: true, color: ICE, fontFace: "Cambria" });
    s.addText(st.d, { x: x + 0.3, y: 2.6, w: colW - 0.6, h: 2.2, fontSize: 13, color: WHITE, valign: "top" });
  });

  s.addText("Full weekly detail and raw data behind every RAG call available on request.",
    { x: 0.9, y: 6.6, w: 11, h: 0.4, fontSize: 12, italic: true, color: ICE });
  pageNum(s, 7);
}

pres.writeFile({ fileName: "Monthly_Executive_Review.pptx" }).then(() => console.log("done"));
