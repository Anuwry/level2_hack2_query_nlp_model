const form = document.querySelector("#queryForm");
const questionInput = document.querySelector("#question");
const submitButton = document.querySelector("#submitButton");
const clearButton = document.querySelector("#clearButton");
const llmToggle = document.querySelector("#llmToggle");
const dateFilter = document.querySelector("#dateFilter");
const cctvFilter = document.querySelector("#cctvFilter");
const startTimeFilter = document.querySelector("#startTimeFilter");
const endTimeFilter = document.querySelector("#endTimeFilter");
const eventFilterButtons = document.querySelectorAll("[data-event-filter]");
const dataCsvSelect = document.querySelector("#dataCsvSelect");
const applyCsvFileButton = document.querySelector("#applyCsvFileButton");
const refreshCsvFilesButton = document.querySelector("#refreshCsvFilesButton");
const dataCsvMeta = document.querySelector("#dataCsvMeta");
const csvForm = document.querySelector("#csvForm");
const csvInput = document.querySelector("#csvInput");
const csvFile = document.querySelector("#csvFile");
const runCsvButton = document.querySelector("#runCsvButton");
const exportCsvButton = document.querySelector("#exportCsvButton");
const clearCsvButton = document.querySelector("#clearCsvButton");
const loadCsvSampleButton = document.querySelector("#loadCsvSampleButton");
const sqlForm = document.querySelector("#sqlForm");
const sqlInput = document.querySelector("#sqlInput");
const sqlFile = document.querySelector("#sqlFile");
const convertSqlButton = document.querySelector("#convertSqlButton");
const exportSqlCsvButton = document.querySelector("#exportSqlCsvButton");
const clearSqlButton = document.querySelector("#clearSqlButton");
const loadSqlSampleButton = document.querySelector("#loadSqlSampleButton");
const statusPill = document.querySelector("#statusPill");
const answerOutput = document.querySelector("#answerOutput");
const jsonOutput = document.querySelector("#jsonOutput");
const csvOutput = document.querySelector("#csvOutput");
const csvAnswerToolbar = document.querySelector("#csvAnswerToolbar");
const csvAnswerMode = document.querySelector("#csvAnswerMode");
const csvAnswerMeta = document.querySelector("#csvAnswerMeta");
const sqlTableSelect = document.querySelector("#sqlTableSelect");
const sqlTableHead = document.querySelector("#sqlTableHead");
const sqlRows = document.querySelector("#sqlRows");
const sqlOutput = document.querySelector("#sqlOutput");
const sqlMeta = document.querySelector("#sqlMeta");
const followUpActions = document.querySelector("#followUpActions");
const countMetric = document.querySelector("#countMetric");
const eventMetric = document.querySelector("#eventMetric");
const routeMetric = document.querySelector("#routeMetric");
const summaryOverview = document.querySelector("#summaryOverview");
const summaryTitle = document.querySelector("#summaryTitle");
const summaryHead = document.querySelector("#summaryPanel thead tr");
const summaryRows = document.querySelector("#summaryRows");
const summaryScopeDate = document.querySelector("#summaryScopeDate");
const summaryScopeCctv = document.querySelector("#summaryScopeCctv");
const summaryScopeStart = document.querySelector("#summaryScopeStart");
const summaryScopeEnd = document.querySelector("#summaryScopeEnd");
const summaryFilterChoices = document.querySelector("#summaryFilterChoices");
const clearSummaryFilterButton = document.querySelector("#clearSummaryFilterButton");
const summaryFilterTotal = document.querySelector("#summaryFilterTotal");
const summaryCompareOutput = document.querySelector("#summaryCompareOutput");
const routeList = document.querySelector("#routeList");
const batchRows = document.querySelector("#batchRows");
const clarificationModal = document.querySelector("#clarificationModal");
const clarificationTitle = document.querySelector("#clarificationTitle");
const clarificationMessage = document.querySelector("#clarificationMessage");
const warningList = document.querySelector("#warningList");
const clarificationSelectLabel = document.querySelector("#clarificationSelectLabel");
const clarificationSelect = document.querySelector("#clarificationSelect");
const applyClarificationButton = document.querySelector("#applyClarificationButton");
const dismissClarificationButton = document.querySelector("#dismissClarificationButton");
const keepCurrentAnswerButton = document.querySelector("#keepCurrentAnswerButton");

let latestResult = null;
let latestBatch = null;
let latestSql = null;
let pendingClarification = null;
let activeWarningKey = null;
let suppressNextOptionalFollowUp = false;
let pendingSummaryMode = null;
let summaryModeOverride = null;
let submitQuestionOnly = false;
let activeCsvPath = "";
let currentSummaryRows = [];
let currentSummaryColumns = [];
let currentSummaryMode = "";
let currentSummaryTitle = "Current breakdown";
let summaryFilterValues = new Set();
let summaryRowScopes = new Map();
let summaryMetadata = { dates: [], cctv_ids: [], colors: [] };
const acknowledgedWarningKeys = new Set();
const csvSample = `Question ID,CCTV ID,Time Range,Query
Q1,CCTVO1,0.01.00 - 0.10.00,จำนวนรถยนต์แยกตามยี่ห้อและสี
Q2,CCTVO1,0.01.00 - 0.10.00,จำนวนรถยนต์แยกตามยี่ห้อ
Q3,CCTVO1,0.01.00 - 0.10.00,จำนวนรถยนต์แยกตามสี`;
const CSV_ANSWER_LABELS = {
  auto: "Auto",
  count: "Count",
  detections: "Detections",
  brand: "Brand",
  color: "Color",
  type: "Type",
  event: "Event",
  origin: "Country",
  brand_color: "Brand × Color",
  origin_brand: "Country × Brand",
  origin_type: "Country × Type",
  brand_type: "Brand × Type",
  camera_event: "Camera × Event",
  hour_event: "Hour × Event",
  color_type: "Color × Type",
  origin_color: "Country × Color",
  route_od: "Start × End",
  brand_route: "Brand × Route",
  unclosed_entry_camera: "Open Entry × Camera",
  routes: "Vehicle Routes",
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  summaryModeOverride = pendingSummaryMode;
  pendingSummaryMode = null;
  const question = questionInput.value.trim();
  const questionOnlySubmit = submitQuestionOnly;
  const filters = questionOnlySubmit ? {} : selectedFilters();
  submitQuestionOnly = false;
  if (!question && !hasSelectedFilters(filters)) {
    renderError("กรุณากรอกคำถาม");
    return;
  }
  if ((filters.start_time && !filters.end_time) || (!filters.start_time && filters.end_time)) {
    renderError("กรุณาเลือกเวลาเริ่มและเวลาสิ้นสุดให้ครบ หรือปล่อยว่างทั้งคู่");
    return;
  }

  submitButton.disabled = true;
  statusPill.textContent = "Querying";
  try {
    const response = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, ...filters, use_llm: questionOnlySubmit ? false : llmToggle.checked }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Query failed");
    }
    latestResult = payload;
    if (Array.isArray(payload.answers)) {
      latestBatch = payload;
      renderBatchResult(payload);
      setTab("csv");
      showFollowUpDialog(payload);
    } else {
      latestBatch = payload.answers_csv ? { answers_csv: payload.answers_csv } : null;
      renderResult(payload);
      showFollowUpDialog(payload);
    }
    statusPill.textContent = "Ready";
  } catch (error) {
    renderError(error.message);
    statusPill.textContent = "Error";
  } finally {
    submitButton.disabled = false;
  }
});

clearButton.addEventListener("click", () => {
  questionInput.value = "";
  dateFilter.value = "";
  cctvFilter.value = "";
  startTimeFilter.value = "";
  endTimeFilter.value = "";
  summaryScopeDate.value = "";
  summaryScopeCctv.value = "";
  summaryScopeStart.value = "";
  summaryScopeEnd.value = "";
  setEventFilter("");
  questionInput.focus();
});

applyCsvFileButton.addEventListener("click", () => {
  selectDataCsv(dataCsvSelect.value);
});

refreshCsvFilesButton.addEventListener("click", () => {
  loadCsvFiles();
});

csvForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const csvText = csvInput.value.trim();
  if (!csvText) {
    renderError("Please paste or upload a CSV question file.");
    return;
  }

  runCsvButton.disabled = true;
  statusPill.textContent = "CSV";
  try {
    const response = await fetch("/api/batch-query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ csv_text: csvText, use_llm: llmToggle.checked }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "CSV query failed");
    }
    latestBatch = payload;
    latestResult = payload;
    renderBatchResult(payload);
    setTab("csv");
    showFollowUpDialog(payload);
    statusPill.textContent = "Ready";
  } catch (error) {
    renderError(error.message);
    statusPill.textContent = "Error";
  } finally {
    runCsvButton.disabled = false;
  }
});

csvFile.addEventListener("change", async () => {
  const [file] = csvFile.files || [];
  if (!file) {
    return;
  }
  csvInput.value = await file.text();
});

loadCsvSampleButton.addEventListener("click", () => {
  csvInput.value = csvSample;
  csvInput.focus();
});

clearCsvButton.addEventListener("click", () => {
  csvInput.value = "";
  csvFile.value = "";
  latestBatch = null;
  exportCsvButton.disabled = true;
  csvOutput.textContent = "Question ID,Answer";
  csvAnswerToolbar.hidden = true;
  csvAnswerMode.innerHTML = "";
  csvAnswerMeta.textContent = "";
  batchRows.innerHTML = "";
});

exportCsvButton.addEventListener("click", () => {
  if (!latestBatch?.answers_csv) {
    return;
  }
  downloadTextFile("cctv_answers.csv", latestBatch.answers_csv, "text/csv;charset=utf-8");
});

sqlForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const sqlText = sqlInput.value.trim();
  if (!sqlText) {
    renderError("Please paste or upload SQL first.");
    return;
  }

  convertSqlButton.disabled = true;
  statusPill.textContent = "SQL";
  try {
    const response = await fetch("/api/sql-to-csv", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sql_text: sqlText }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "SQL conversion failed");
    }
    latestSql = payload;
    latestResult = payload;
    renderSqlResult(payload);
    jsonOutput.textContent = JSON.stringify(payload, null, 2);
    setTab("sql");
    statusPill.textContent = "Ready";
  } catch (error) {
    renderError(error.message);
    statusPill.textContent = "Error";
  } finally {
    convertSqlButton.disabled = false;
  }
});

sqlFile.addEventListener("change", async () => {
  const [file] = sqlFile.files || [];
  if (!file) {
    return;
  }
  sqlInput.value = await file.text();
});

loadSqlSampleButton.addEventListener("click", async () => {
  statusPill.textContent = "Loading";
  try {
    const response = await fetch("/api/sql-sample");
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Could not load SQL sample");
    }
    sqlInput.value = [payload.schema_sql, payload.examples_sql].filter(Boolean).join("\n\n");
    sqlInput.focus();
    statusPill.textContent = "Ready";
  } catch (error) {
    renderError(error.message);
    statusPill.textContent = "Error";
  }
});

clearSqlButton.addEventListener("click", () => {
  sqlInput.value = "";
  sqlFile.value = "";
  latestSql = null;
  exportSqlCsvButton.disabled = true;
  sqlTableSelect.innerHTML = "";
  sqlTableHead.innerHTML = "";
  sqlRows.innerHTML = "";
  sqlOutput.textContent = "";
  sqlMeta.textContent = "No SQL table";
});

exportSqlCsvButton.addEventListener("click", () => {
  const table = selectedSqlTable();
  if (!table?.csv) {
    return;
  }
  downloadTextFile(`${table.name}.csv`, table.csv, "text/csv;charset=utf-8");
});

sqlTableSelect.addEventListener("change", renderSelectedSqlTable);

applyClarificationButton.addEventListener("click", () => {
  if (!pendingClarification) {
    closeClarificationModal();
    return;
  }
  const option = pendingClarification.options[Number(clarificationSelect.value)];
  const nextQuestion = buildClarifiedQuestion(
    pendingClarification.result,
    pendingClarification.clarification,
    option
  );
  suppressNextOptionalFollowUp = true;
  closeClarificationModal();
  questionInput.value = nextQuestion;
  form.requestSubmit();
});

dismissClarificationButton.addEventListener("click", closeClarificationModal);
keepCurrentAnswerButton.addEventListener("click", closeClarificationModal);

clarificationModal.addEventListener("click", (event) => {
  if (event.target === clarificationModal) {
    closeClarificationModal();
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !clarificationModal.hidden) {
    closeClarificationModal();
  }
});

document.querySelectorAll("[data-tab]").forEach((button) => {
  button.addEventListener("click", () => setTab(button.dataset.tab));
});

document.querySelectorAll("[data-summary-mode][data-question]").forEach((button) => {
  button.addEventListener("click", () => runPresetQuestion(button.dataset.question || "", button.dataset.summaryMode || null));
});

eventFilterButtons.forEach((button) => {
  button.addEventListener("click", () => setEventFilter(button.dataset.eventFilter || ""));
});

csvAnswerMode.addEventListener("change", () => {
  if (latestResult && !Array.isArray(latestResult.answers)) {
    updateSingleCsvAnswer(latestResult, csvAnswerMode.value);
  }
});

clearSummaryFilterButton.addEventListener("click", () => {
  summaryFilterValues = new Set();
  renderSummaryFromState(true);
});

summaryRows.addEventListener("click", (event) => {
  const button = event.target.closest("[data-summary-row-calc]");
  if (!button) {
    return;
  }
  calculateSummaryRow(button.dataset.summaryRowCalc || "");
});

summaryRows.addEventListener("change", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const key = target.dataset.summaryRowKey || "";
  if (!key) {
    return;
  }
  if (target.classList.contains("summary-row-compare")) {
    updateSummaryRowCompare(key, target.checked);
    return;
  }
  if (target.dataset.summaryScopeField) {
    updateSummaryRowScope(key, target.dataset.summaryScopeField, target.value || "");
  }
});

followUpActions.addEventListener("click", (event) => {
  const button = event.target.closest("[data-followup-question]");
  if (!button) {
    return;
  }
  submitQuestionOnly = true;
  runPresetQuestion(button.dataset.followupQuestion || "", button.dataset.summaryMode || null);
});

loadCsvFiles();
loadMetadata();

function runPresetQuestion(question, summaryMode) {
  pendingSummaryMode = summaryMode;
  questionInput.value = question;
  form.requestSubmit();
}

function setTab(tabName) {
  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  document.querySelectorAll("[data-panel]").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.panel === tabName);
  });
}

function renderResult(result) {
  answerOutput.classList.remove("error");
  answerOutput.textContent = answerText(result);
  jsonOutput.textContent = JSON.stringify(result, null, 2);
  renderCsvAnswerModeSelector(result);
  updateSingleCsvAnswer(result, csvAnswerMode.value || "auto");
  countMetric.textContent = result.count ?? 0;
  eventMetric.textContent = result.event_count ?? 0;
  routeMetric.textContent = Array.isArray(result.routes) ? result.routes.length : 0;
  renderSummaryOverview(result);
  syncSummaryScopeFromQuery(result.query || {});
  const mode = summaryModeForResult(result);
  renderSummary(summaryTableRows(result), summaryTableColumns(result), summaryModeLabel(mode), mode);
  renderFollowUpActions(result);
  renderRoutes(result.routes || []);
}

function renderBatchResult(batch) {
  const rows = batch.answers || [];
  answerOutput.classList.remove("error");
  answerOutput.textContent = rows
    .map((row) => `${row.question_id}: ${row.answer}\nCSV: ${row.csv_answer}`)
    .join("\n\n");
  jsonOutput.textContent = JSON.stringify(batch, null, 2);
  csvOutput.textContent = batch.answers_csv || "Question ID,Answer";
  csvAnswerToolbar.hidden = true;
  csvAnswerMode.innerHTML = "";
  csvAnswerMeta.textContent = "";
  countMetric.textContent = rows.length;
  eventMetric.textContent = rows.reduce((total, row) => total + (row.event_count || 0), 0);
  routeMetric.textContent = "-";
  followUpActions.hidden = true;
  followUpActions.innerHTML = "";
  summaryOverview.innerHTML = "";
  summaryTitle.textContent = "Current breakdown";
  summaryHead.innerHTML = "<th>Group</th><th>Value</th><th>Count</th>";
  summaryRows.innerHTML = "";
  resetSummaryFilter();
  renderBatchRows(rows);
  exportCsvButton.disabled = !batch.answers_csv;
}

function renderCsvAnswerModeSelector(result) {
  const modes = availableCsvAnswerModes(result);
  csvAnswerMode.innerHTML = modes
    .map((mode) => `<option value="${escapeHtml(mode)}">${escapeHtml(CSV_ANSWER_LABELS[mode] || mode)}</option>`)
    .join("");
  csvAnswerMode.value = modes.includes("auto") ? "auto" : modes[0] || "";
  csvAnswerToolbar.hidden = modes.length <= 1;
  csvAnswerMeta.textContent = csvAnswerMode.value ? "เลือกได้จาก summary เดิม" : "";
}

function availableCsvAnswerModes(result) {
  const modes = ["auto", "count", "detections"];
  const summary = result.summary || {};
  if (hasNamedCounts(summary.brand_counts)) modes.push("brand");
  if (hasNamedCounts(summary.color_counts)) modes.push("color");
  if (hasNamedCounts(summary.type_counts)) modes.push("type");
  if (hasNamedCounts(summary.event_counts)) modes.push("event");
  if (hasNamedCounts(summary.origin_counts)) modes.push("origin");
  if ((summary.brand_color_counts || []).length) modes.push("brand_color");
  Object.keys(CSV_ANSWER_LABELS)
    .filter((mode) => CROSS_SUMMARY_MODES.has(mode))
    .forEach((mode) => {
      if ((summary.cross_counts?.[mode] || []).length) {
        modes.push(mode);
      }
    });
  if ((result.routes || []).length) {
    modes.push("routes");
  }
  return [...new Set(modes)];
}

function updateSingleCsvAnswer(result, mode) {
  const csvAnswer = csvAnswerForMode(result, mode);
  const row = {
    question_id: result.question_id || "Q1",
    answer: result.answer || "",
    csv_answer: csvAnswer,
  };
  const answersCsv = renderAnswersCsv([row]);
  csvOutput.textContent = answersCsv;
  renderBatchRows([row]);
  latestBatch = { answers_csv: answersCsv };
  exportCsvButton.disabled = false;
  csvAnswerMeta.textContent = mode === "auto" ? "จากคำถามเดิม" : CSV_ANSWER_LABELS[mode] || mode;
}

function csvAnswerForMode(result, mode) {
  const summary = result.summary || {};
  if (mode === "auto") return result.csv_answer || "";
  if (mode === "count") return String(result.count ?? 0);
  if (mode === "detections") return String(result.event_count ?? 0);
  if (mode === "brand") return formatNamedCounts(summary.brand_counts);
  if (mode === "color") return formatNamedCounts(summary.color_counts);
  if (mode === "type") return formatNamedCounts(summary.type_counts);
  if (mode === "event") return formatNamedCounts(summary.event_counts, ["entry", "exit", "pass"]);
  if (mode === "origin") return formatNamedCounts(summary.origin_counts);
  if (mode === "brand_color") {
    return formatPairRows(summary.brand_color_counts || [], "brand", "color");
  }
  if (CROSS_SUMMARY_MODES.has(mode)) {
    return formatPairRows(summary.cross_counts?.[mode] || [], "left", "right");
  }
  if (mode === "routes") {
    return formatRouteRows(result.routes || []);
  }
  return result.csv_answer || "";
}

function hasNamedCounts(counts) {
  return Object.keys(counts || {}).length > 0;
}

function formatNamedCounts(counts, preferredOrder = []) {
  const entries = Object.entries(counts || {});
  const order = new Map(preferredOrder.map((name, index) => [name, index]));
  const sorted = entries.sort((a, b) => {
    const orderA = order.has(a[0]) ? order.get(a[0]) : Number.MAX_SAFE_INTEGER;
    const orderB = order.has(b[0]) ? order.get(b[0]) : Number.MAX_SAFE_INTEGER;
    return orderA - orderB || Number(b[1]) - Number(a[1]) || String(a[0]).localeCompare(String(b[0]));
  });
  return "[" + sorted.map(([name, count]) => `${name}:${count}`).join(", ") + "]";
}

function formatPairRows(rows, leftKey, rightKey) {
  const sorted = [...rows].sort(
    (a, b) =>
      Number(b.count) - Number(a.count) ||
      String(a[leftKey]).localeCompare(String(b[leftKey])) ||
      String(a[rightKey]).localeCompare(String(b[rightKey]))
  );
  return "[" + sorted.map((row) => `(${row[leftKey]}, ${row[rightKey]}):${row.count}`).join(", ") + "]";
}

function formatRouteRows(routes) {
  return (
    "[" +
    routes
      .map((route, index) => {
        const label = `${route.brand} ${route.color} ${route.type}`;
        const path = (route.path || []).join("->");
        return `${index + 1}:${label} ${route.start_time}-${route.end_time} ${path}`;
      })
      .join(", ") +
    "]"
  );
}

function renderAnswersCsv(rows) {
  return ["Question ID,Answer", ...rows.map((row) => `${csvCell(row.question_id)},${csvCell(row.csv_answer)}`)].join("\n") + "\n";
}

function csvCell(value) {
  const text = String(value ?? "");
  if (/[",\n\r]/.test(text)) {
    return `"${text.replaceAll('"', '""')}"`;
  }
  return text;
}

function renderSqlResult(payload) {
  const tables = payload.tables || [];
  sqlTableSelect.innerHTML = "";
  tables.forEach((table) => {
    const option = document.createElement("option");
    option.value = table.name;
    option.textContent = `${table.name} (${table.row_count || 0})`;
    sqlTableSelect.appendChild(option);
  });
  sqlTableSelect.value = payload.selected_table || tables[0]?.name || "";
  renderSelectedSqlTable();
}

function selectedSqlTable() {
  const tables = latestSql?.tables || [];
  return tables.find((table) => table.name === sqlTableSelect.value) || tables[0] || null;
}

function renderSelectedSqlTable() {
  const table = selectedSqlTable();
  sqlTableHead.innerHTML = "";
  sqlRows.innerHTML = "";
  sqlOutput.textContent = "";
  exportSqlCsvButton.disabled = true;

  if (!table) {
    sqlMeta.textContent = "No SQL table";
    return;
  }

  sqlMeta.textContent = `${table.row_count || 0} rows`;
  const headerRow = document.createElement("tr");
  (table.columns || []).forEach((column) => {
    const cell = document.createElement("th");
    cell.textContent = column;
    headerRow.appendChild(cell);
  });
  sqlTableHead.appendChild(headerRow);

  (table.rows || []).forEach((item) => {
    const row = document.createElement("tr");
    (table.columns || []).forEach((column) => {
      const cell = document.createElement("td");
      cell.textContent = item[column] ?? "";
      row.appendChild(cell);
    });
    sqlRows.appendChild(row);
  });

  sqlOutput.textContent = table.csv || "";
  exportSqlCsvButton.disabled = !table.csv;
}

function answerText(result) {
  const lines = [];
  const normalization = result.llm_normalization || {};
  if (normalization.used && normalization.changed) {
    lines.push(`Normalized: ${result.normalized_question || normalization.normalized_question}`);
    lines.push("");
  }
  if (normalization.error) {
    lines.push(`LLM fallback: ${normalization.error}`);
    lines.push("");
  }
  lines.push(result.answer || "");
  if (Array.isArray(result.answer_options) && result.answer_options.length) {
    lines.push("");
    lines.push("คำตอบทางเลือก:");
    result.answer_options.forEach((option, index) => {
      const csv = option.csv_answer ? ` | CSV: ${option.csv_answer}` : "";
      lines.push(`${index + 1}. ${option.answer || option.label || option.id}${csv}`);
    });
  }
  return lines.join("\n");
}

function renderFollowUpActions(result) {
  const actions = followUpActionsForResult(result);
  if (!actions.length) {
    followUpActions.hidden = true;
    followUpActions.innerHTML = "";
    return;
  }

  followUpActions.innerHTML = [
    '<span class="follow-up-label">ใช้ต่อ:</span>',
    ...actions.map((action) => followUpButtonHtml(action)),
  ].join("");
  followUpActions.hidden = false;
}

function followUpActionsForResult(result) {
  const mode = summaryModeForResult(result);
  const query = result.query || {};
  const eventFocused = mode === "event" || mode === "camera_event" || mode === "hour_event" || Boolean(query.event);
  const withContext = (action) => ({
    ...action,
    question: buildFollowUpQuestion(query, action),
  });
  if (!eventFocused) {
    return [
      { label: "ดู Event", question: "รถทั้งหมดตาม event", mode: "event" },
      { label: "ดู Type", question: "รถทั้งหมดตามประเภทรถ", mode: "type" },
      { label: "ดู Color", question: "รถทั้งหมดตามสี", mode: "color" },
      { label: "ดู Country", question: "รถทั้งหมดตามประเทศ", mode: "origin" },
      { label: "Country × Brand", question: "รถทั้งหมดตามประเทศและยี่ห้อ", mode: "origin_brand" },
      { label: "Country × Type", question: "รถทั้งหมดตามประเทศและประเภทรถ", mode: "origin_type" },
      { label: "Country × Color", question: "รถทั้งหมดตามประเทศและสี", mode: "origin_color" },
      { label: "Brand × Type", question: "รถทั้งหมดตามยี่ห้อและประเภทรถ", mode: "brand_type" },
      { label: "Color × Type", question: "รถทั้งหมดตามสีและประเภทรถ", mode: "color_type" },
      { label: "Brand × Route", question: "แต่ละยี่ห้อใช้เส้นทางไหนบ่อยสุด", mode: "brand_route" },
      { label: "Start × End", question: "รถเดินทางจากกล้องไหนไปกล้องไหนมากที่สุด", mode: "route_od" },
    ].filter((action) => followUpActionConnects(query, action, mode)).map(withContext);
  }

  return [
    { label: "Camera × Event", question: "แต่ละกล้องมี entry exit pass เท่าไหร่", mode: "camera_event" },
    { label: "Hour × Event", question: "แต่ละชั่วโมงมีรถเข้าออกกี่คัน", mode: "hour_event" },
    { label: "เฉพาะ entry", question: "event entry vehicles", mode: "event" },
    { label: "เฉพาะ exit", question: "event exit vehicles", mode: "event" },
    { label: "เฉพาะ pass", question: "event pass vehicles", mode: "event" },
    { label: "entry ไม่ exit", question: "entry without exit", mode: "event" },
    { label: "entry ไม่ exit × กล้อง", question: "รถที่ entry แล้วไม่ exit แยกตามกล้อง entry", mode: "unclosed_entry_camera" },
  ].filter((action) => followUpActionConnects(query, action, mode)).map(withContext);
}

function buildFollowUpQuestion(query, action) {
  const actionQuestion = String(action.question || "").toLowerCase();
  const inferredEvent =
    action.event ||
    (actionQuestion.includes("event entry") ? "entry" : "") ||
    (actionQuestion.includes("event exit") ? "exit" : "") ||
    (actionQuestion.includes("event pass") ? "pass" : "");
  return buildStructuredQuestion(query, {
    mode: action.mode,
    event: inferredEvent,
    unclosedEntry: action.unclosedEntry || action.mode === "unclosed_entry_camera" || actionQuestion.includes("entry without exit"),
  });
}

function followUpActionConnects(query, action, currentMode) {
  if (!hasFollowUpContext(query)) {
    return false;
  }
  if (action.mode === currentMode && !action.event && !action.unclosedEntry) {
    return false;
  }

  switch (action.mode) {
    case "origin_brand":
      return hasOriginContext(query) || hasBrandContext(query);
    case "origin_type":
      return hasOriginContext(query) || hasTypeContext(query);
    case "origin_color":
      return hasOriginContext(query) || hasColorContext(query);
    case "brand_type":
      return hasBrandContext(query) || hasTypeContext(query);
    case "color_type":
      return hasColorContext(query) || hasTypeContext(query);
    case "brand_route":
      return hasBrandContext(query);
    case "route_od":
      return hasVehicleContext(query) && !query.cctv_id;
    case "camera_event":
      return hasEventContext(query) && !query.cctv_id;
    case "hour_event":
      return hasEventContext(query);
    case "unclosed_entry_camera":
      return !query.cctv_id && (hasEventContext(query) || hasVehicleContext(query));
    default:
      return false;
  }
}

function hasFollowUpContext(query) {
  return Boolean(
    query.date ||
      query.cctv_id ||
      query.start_time ||
      query.end_time ||
      hasVehicleContext(query) ||
      hasEventContext(query)
  );
}

function hasVehicleContext(query) {
  return hasBrandContext(query) || hasOriginContext(query) || hasColorContext(query) || hasTypeContext(query);
}

function hasBrandContext(query) {
  return Boolean(query.brand || (Array.isArray(query.brands) && query.brands.length));
}

function hasOriginContext(query) {
  const crossBreakdowns = query.cross_breakdowns || [];
  return Boolean(
    (Array.isArray(query.brand_origins) && query.brand_origins.length) ||
      query.wants_origin_breakdown ||
      query.wants_origin_brand_breakdown ||
      crossBreakdowns.some((name) => String(name).startsWith("origin_"))
  );
}

function hasColorContext(query) {
  return Boolean(query.color || (Array.isArray(query.colors) && query.colors.length));
}

function hasTypeContext(query) {
  return Boolean(query.vehicle_type);
}

function hasEventContext(query) {
  const crossBreakdowns = query.cross_breakdowns || [];
  return Boolean(
    query.event ||
      (Array.isArray(query.events) && query.events.length) ||
      query.wants_event_breakdown ||
      query.wants_unclosed_entry_count ||
      crossBreakdowns.includes("camera_event") ||
      crossBreakdowns.includes("hour_event") ||
      crossBreakdowns.includes("unclosed_entry_camera")
  );
}

function followUpButtonHtml(action) {
  return `
    <button
      type="button"
      class="quick-chip"
      data-followup-question="${escapeHtml(action.question)}"
      data-summary-mode="${escapeHtml(action.mode || "")}"
      title="${escapeHtml(action.question)}"
    >${escapeHtml(action.label)}</button>
  `;
}

function showFollowUpDialog(payload) {
  if (Array.isArray(payload.answers)) {
    showBatchFollowUpDialog(payload.answers);
    return;
  }

  const clarifications = payload.clarifications || [];
  const warnings = payload.warnings || [];
  const requiredClarification = clarifications.find((item) => item.required);
  if (requiredClarification) {
    suppressNextOptionalFollowUp = false;
    openClarificationDialog("เลือกข้อมูลเพิ่มเติม", requiredClarification, warnings, payload);
    return;
  }

  if (suppressNextOptionalFollowUp) {
    suppressNextOptionalFollowUp = false;
    return;
  }

  const colorClarification = clarifications.find((item) => item.field === "color");
  if (colorClarification) {
    openClarificationDialog("เลือกสีที่ต้องการ", colorClarification, warnings, payload);
    return;
  }

  if (warnings.length) {
    openWarningDialogIfNeeded("คำถามค้นหากว้าง", warnings, warningDialogKey(payload, warnings));
  }
}

function showBatchFollowUpDialog(rows) {
  const requiredRows = rows.filter((row) => row.needs_clarification);
  if (requiredRows.length) {
    openWarningDialog(
      "ต้องระบุข้อมูลเพิ่ม",
      requiredRows.map((row) => `${row.question_id}: ${firstClarificationMessage(row)}`)
    );
    return;
  }

  const warnings = [];
  rows.forEach((row) => {
    (row.warnings || []).forEach((warning) => warnings.push(`${row.question_id}: ${warning}`));
  });
  if (warnings.length) {
    openWarningDialogIfNeeded("คำถามค้นหากว้าง", warnings, batchWarningDialogKey(rows, warnings));
  }
}

function firstClarificationMessage(row) {
  const [clarification] = row.clarifications || [];
  return clarification?.message || "Please clarify this row.";
}

function openClarificationDialog(title, clarification, warnings, result) {
  activeWarningKey = null;
  pendingClarification = {
    result,
    clarification,
    options: clarification.options || [],
  };
  clarificationTitle.textContent = title;
  clarificationMessage.textContent = clarification.message || "";
  renderWarningList(warnings);
  clarificationSelectLabel.hidden = false;
  clarificationSelect.hidden = false;
  applyClarificationButton.hidden = false;
  keepCurrentAnswerButton.hidden = false;
  keepCurrentAnswerButton.textContent = clarification.required ? "ยกเลิก" : "ใช้คำตอบปัจจุบัน";
  renderClarificationOptions(pendingClarification.options);
  clarificationModal.hidden = false;
  clarificationSelect.focus();
}

function openWarningDialogIfNeeded(title, warnings, key) {
  if (suppressNextOptionalFollowUp || acknowledgedWarningKeys.has(key)) {
    suppressNextOptionalFollowUp = false;
    return;
  }
  openWarningDialog(title, warnings, key);
}

function openWarningDialog(title, warnings, key) {
  pendingClarification = null;
  activeWarningKey = key || warningDialogKey(latestResult || {}, warnings);
  clarificationTitle.textContent = title;
  clarificationMessage.textContent = "";
  renderWarningList(warnings);
  clarificationSelectLabel.hidden = true;
  clarificationSelect.hidden = true;
  applyClarificationButton.hidden = true;
  keepCurrentAnswerButton.hidden = false;
  keepCurrentAnswerButton.textContent = "รับทราบ";
  clarificationModal.hidden = false;
  keepCurrentAnswerButton.focus();
}

function closeClarificationModal() {
  if (activeWarningKey) {
    acknowledgedWarningKeys.add(activeWarningKey);
  }
  pendingClarification = null;
  activeWarningKey = null;
  clarificationModal.hidden = true;
}

function warningDialogKey(payload, warnings) {
  const questionKey = payload.normalized_question || payload.original_question || payload.answer || questionInput.value.trim();
  return `${questionKey}::${(warnings || []).join("|")}`;
}

function batchWarningDialogKey(rows, warnings) {
  const rowKey = (rows || []).map((row) => row.question_id || row.composed_question || row.query || "").join("|");
  return `${rowKey}::${(warnings || []).join("|")}`;
}

function renderWarningList(warnings) {
  warningList.innerHTML = "";
  (warnings || []).forEach((warning) => {
    const item = document.createElement("li");
    item.textContent = warning;
    warningList.appendChild(item);
  });
  warningList.hidden = !warnings?.length;
}

function renderClarificationOptions(options) {
  clarificationSelect.innerHTML = "";
  options.forEach((option, index) => {
    const item = document.createElement("option");
    item.value = String(index);
    item.textContent = optionLabel(option);
    clarificationSelect.appendChild(item);
  });
}

function optionLabel(option) {
  const label = option.label || option.value || "";
  return typeof option.count === "number" ? `${label} (${option.count})` : label;
}

function buildClarifiedQuestion(result, clarification, option) {
  const override = {};
  if (clarification.field === "date") {
    override.date = option.date || option.value;
  }
  if (clarification.field === "color") {
    override.colors = option.colors || [option.value];
  }
  return buildStructuredQuestion(result.query || {}, override);
}

function buildStructuredQuestion(query, override = {}) {
  const parts = [];
  const replacingIntent = Boolean(override.mode || override.event || override.unclosedEntry);
  if (Array.isArray(query.condition_groups) && query.condition_groups.length) {
    parts.push(query.condition_groups.map(conditionGroupPhrase).join(" or "));
  }
  const date = override.date || query.date;
  if (date) {
    parts.push(`date ${date}`);
  }
  if (query.cctv_id) {
    parts.push(query.cctv_id);
  }
  if (query.start_time && query.end_time) {
    parts.push(`from ${query.start_time} to ${query.end_time}`);
  }
  const queryBrands = Array.isArray(query.brands) && query.brands.length ? query.brands : (query.brand ? [query.brand] : []);
  if (queryBrands.length) {
    parts.push(`brand ${queryBrands.join(" and ")}`);
  }
  if (Array.isArray(query.brand_origins) && query.brand_origins.length) {
    parts.push(`origin ${query.brand_origins.join(" and ")}`);
  }
  const queryColors = Array.isArray(query.colors) && query.colors.length ? query.colors : (query.color ? [query.color] : []);
  const colors = override.colors || queryColors;
  if (colors.length) {
    parts.push(`color ${colors.join(" and ")}`);
  }
  if (query.vehicle_type) {
    parts.push(`type ${query.vehicle_type}`);
  }
  if (override.event) {
    parts.push(`event ${override.event}`);
  } else if (!replacingIntent && query.event) {
    parts.push(`event ${query.event}`);
  }
  if (!replacingIntent && Array.isArray(query.events) && query.events.length) {
    parts.push(`events ${query.events.join(" and ")}`);
  }
  if (query.wants_distinct_vehicle_count) {
    parts.push("distinct vehicles");
  }
  if (query.count_operator && Number.isFinite(Number(query.count_threshold))) {
    parts.push(`${countOperatorSymbol(query.count_operator)} ${query.count_threshold}`);
  }
  if (override.unclosedEntry && override.mode !== "unclosed_entry_camera") {
    parts.push("entry without exit");
  } else if (!replacingIntent && query.wants_unclosed_entry_count) {
    parts.push("entry without exit");
  }
  if (!replacingIntent && query.wants_event_breakdown) {
    parts.push("by event");
  }
  if (!replacingIntent && query.wants_peak_hour) {
    parts.push("busiest hour");
  }
  if (!replacingIntent && query.wants_peak_camera) {
    parts.push("busiest camera");
  }
  if (!replacingIntent && query.wants_hour_breakdown) {
    parts.push("by hour");
  }
  if (!replacingIntent && query.wants_camera_breakdown) {
    parts.push("by camera");
  }
  if (!replacingIntent && query.wants_vehicle_list) {
    parts.push("list vehicles");
  }
  if (!replacingIntent && query.wants_route) {
    parts.push("route");
  }
  if (override.mode && !override.event && !(override.unclosedEntry && override.mode === "event")) {
    parts.push(followUpModeQuestionPhrase(override.mode));
  } else if (!replacingIntent && Array.isArray(query.cross_breakdowns) && query.cross_breakdowns.length) {
    parts.push(crossBreakdownQuestionPhrase(query.cross_breakdowns[0]));
  } else if (!replacingIntent && query.wants_origin_brand_breakdown) {
    parts.push("by country and brand");
  } else if (!replacingIntent && query.wants_origin_breakdown) {
    parts.push("by country");
  } else if (!replacingIntent && query.wants_brand_color_breakdown) {
    parts.push("by brand and color");
  }
  return parts.join(" ") || query.raw_question || questionInput.value.trim();
}

function countOperatorSymbol(operator) {
  return {
    gt: ">",
    gte: ">=",
    lt: "<",
    lte: "<=",
    eq: "=",
  }[operator] || operator;
}

function conditionGroupPhrase(group) {
  const parts = [];
  if (group.date) {
    parts.push(`date ${group.date}`);
  }
  if (group.start_time && group.end_time) {
    parts.push(`from ${group.start_time} to ${group.end_time}`);
  }
  const brands = Array.isArray(group.brands) ? group.brands : (group.brand ? [group.brand] : []);
  if (brands.length) {
    parts.push(`brand ${brands.join(" and ")}`);
  }
  const colors = Array.isArray(group.colors) ? group.colors : (group.color ? [group.color] : []);
  if (colors.length) {
    parts.push(`color ${colors.join(" and ")}`);
  }
  if (group.vehicle_type) {
    parts.push(`type ${group.vehicle_type}`);
  }
  if (group.event) {
    parts.push(`event ${group.event}`);
  }
  return parts.join(" ");
}

function crossBreakdownQuestionPhrase(name) {
  return {
    origin_brand: "by country and brand",
    origin_type: "by country and type",
    brand_type: "by brand and type",
    camera_event: "by camera and event",
    hour_event: "by hour and event",
    color_type: "by color and type",
    origin_color: "by country and color",
    route_od: "by route start and end",
    brand_route: "by brand and route",
    unclosed_entry_camera: "entry without exit by camera",
  }[name] || name;
}

function followUpModeQuestionPhrase(mode) {
  if (CROSS_SUMMARY_MODES.has(mode)) {
    return crossBreakdownQuestionPhrase(mode);
  }
  return {
    brand: "by brand",
    color: "by color",
    type: "by type",
    event: "by event",
    origin: "by country",
    brand_color: "by brand and color",
  }[mode] || mode;
}

function selectedFilters() {
  return {
    date: dateFilter.value,
    cctv_id: cctvFilter.value,
    start_time: startTimeFilter.value,
    end_time: endTimeFilter.value,
    event: selectedEventFilter(),
  };
}

function hasSelectedFilters(filters) {
  return Boolean(filters.date || filters.cctv_id || filters.start_time || filters.end_time || filters.event);
}

function selectedEventFilter() {
  const active = document.querySelector("[data-event-filter].active");
  return active?.dataset.eventFilter || "";
}

function setEventFilter(value) {
  eventFilterButtons.forEach((button) => {
    const selected = (button.dataset.eventFilter || "") === value;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", selected ? "true" : "false");
  });
}

async function loadMetadata() {
  try {
    const response = await fetch("/api/metadata");
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Could not load filters");
    }
    summaryMetadata = {
      dates: payload.dates || [],
      cctv_ids: payload.cctv_ids || [],
      colors: payload.colors || [],
    };
    populateSelect(dateFilter, payload.dates || [], "ทุกวันที่");
    populateSelect(cctvFilter, payload.cctv_ids || [], "ทุกกล้อง");
    populateSelect(summaryScopeDate, payload.dates || [], "วันที่เดิม");
    populateSelect(summaryScopeCctv, payload.cctv_ids || [], "กล้องเดิม");
  } catch (error) {
    console.warn(error.message);
  }
}

async function loadCsvFiles() {
  refreshCsvFilesButton.disabled = true;
  dataCsvMeta.textContent = "Loading CSV files...";
  try {
    const response = await fetch("/api/csv-files");
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Could not load CSV files");
    }
    renderDataCsvFiles(payload);
  } catch (error) {
    dataCsvMeta.textContent = error.message;
  } finally {
    refreshCsvFilesButton.disabled = false;
  }
}

function renderDataCsvFiles(payload) {
  const files = payload.files || [];
  activeCsvPath = payload.active_csv || "";
  dataCsvSelect.innerHTML = "";
  files.forEach((file) => {
    const option = document.createElement("option");
    option.value = file.path;
    option.disabled = !file.loadable;
    option.textContent = file.loadable
      ? `${file.path} (${file.row_count} rows)`
      : `${file.path} (not data CSV)`;
    option.title = file.error || file.absolute_path || file.path;
    dataCsvSelect.appendChild(option);
  });
  if (activeCsvPath) {
    dataCsvSelect.value = activeCsvPath;
  }
  const loadableCount = files.filter((file) => file.loadable).length;
  applyCsvFileButton.disabled = !loadableCount;
  dataCsvMeta.textContent = activeCsvPath
    ? `Active: ${activeCsvPath} | ${loadableCount}/${files.length} CSV files loadable`
    : `${loadableCount}/${files.length} CSV files loadable`;
}

async function selectDataCsv(path) {
  if (!path) {
    renderError("Please select a CSV file.");
    return;
  }
  applyCsvFileButton.disabled = true;
  statusPill.textContent = "Loading CSV";
  try {
    const response = await fetch("/api/select-csv", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Could not switch CSV");
    }
    activeCsvPath = payload.active_csv || path;
    await loadMetadata();
    await loadCsvFiles();
    renderNotice(`ใช้ CSV: ${activeCsvPath}`);
    statusPill.textContent = "Ready";
  } catch (error) {
    renderError(error.message);
    statusPill.textContent = "Error";
  } finally {
    applyCsvFileButton.disabled = false;
  }
}

function populateSelect(select, values, emptyLabel) {
  const currentValue = select.value;
  select.innerHTML = "";
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = emptyLabel;
  select.appendChild(empty);
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
  if (values.includes(currentValue)) {
    select.value = currentValue;
  }
}

function summaryModeForResult(result) {
  if (summaryModeOverride) {
    return summaryModeOverride;
  }
  const [crossName] = result.query?.cross_breakdowns || [];
  if (crossName) {
    return crossName;
  }
  const inferred = inferSummaryModeFromQuestion(result.query?.raw_question || result.original_question || "");
  if (inferred) {
    return inferred;
  }
  if (result.query?.wants_event_breakdown) {
    return "event";
  }
  if (result.query?.wants_origin_breakdown) {
    return "origin";
  }
  if (result.query?.wants_brand_color_breakdown) {
    return "brand_color";
  }
  return "brand";
}

function inferSummaryModeFromQuestion(question) {
  const text = String(question || "").toLowerCase();
  const has = (terms) => terms.some((term) => text.includes(term));
  const origin = has(["country", "origin", "region", "ประเทศ", "สัญชาติ"]);
  const brand = has(["brand", "ยี่ห้อ"]);
  const color = has(["color", "colour", "สี"]);
  const type = has(["type", "ประเภทรถ", "ประเภท"]);
  const event = has(["event", "entry", "exit", "pass", "เข้า", "ออก", "ผ่าน"]);
  const camera = has(["camera", "cctv", "กล้อง"]);
  const hour = has(["hour", "time", "ชั่วโมง", "เวลา"]);
  const route = has(["route", "path", "เส้นทาง", "เดินทาง"]);
  const startEnd = has(["start", "end", "from", "to", "ต้นทาง", "ปลายทาง", "จาก", "ไป"]);

  if (origin && brand) return "origin_brand";
  if (origin && type) return "origin_type";
  if (brand && type) return "brand_type";
  if (camera && event) return "camera_event";
  if (hour && event) return "hour_event";
  if (color && type) return "color_type";
  if (origin && color) return "origin_color";
  if (route && startEnd) return "route_od";
  if (brand && route) return "brand_route";
  if (origin) return "origin";
  if (brand && color) return "brand_color";
  if (brand) return "brand";
  if (color) return "color";
  if (type) return "type";
  if (event) return "event";
  return null;
}

function summaryTableRows(result) {
  const mode = summaryModeForResult(result);
  if (CROSS_SUMMARY_MODES.has(mode)) {
    return result.summary?.cross_counts?.[mode] || [];
  }
  if (mode === "brand_color") return result.summary?.brand_color_counts || [];
  if (mode === "brand") return namedSummaryRows(result.summary?.brand_counts);
  if (mode === "color") return namedSummaryRows(result.summary?.color_counts);
  if (mode === "type") return namedSummaryRows(result.summary?.type_counts);
  if (mode === "event") return namedSummaryRows(result.summary?.event_counts);
  if (mode === "origin") return namedSummaryRows(result.summary?.origin_counts);
  return result.summary?.brand_color_counts || [];
}

function summaryTableColumns(result) {
  const mode = summaryModeForResult(result);
  if (CROSS_SUMMARY_MODES.has(mode)) {
    const labels = crossBreakdownColumnLabels(mode);
    return [
      { key: "left", label: labels[0] },
      { key: "right", label: labels[1] },
      { key: "count", label: "Count" },
    ];
  }
  if (mode === "brand_color") {
    return [
      { key: "brand", label: "Brand" },
      { key: "color", label: "Color" },
      { key: "count", label: "Count" },
    ];
  }
  return [
    { key: "name", label: summaryModeLabel(mode) },
    { key: "count", label: "Count" },
  ];
}

const CROSS_SUMMARY_MODES = new Set([
  "origin_brand",
  "origin_type",
  "brand_type",
  "camera_event",
  "hour_event",
  "color_type",
  "origin_color",
  "route_od",
  "brand_route",
  "unclosed_entry_camera",
]);

function crossBreakdownColumnLabels(name) {
  return {
    origin_brand: ["Origin", "Brand"],
    origin_type: ["Origin", "Type"],
    brand_type: ["Brand", "Type"],
    camera_event: ["Camera", "Event"],
    hour_event: ["Hour", "Event"],
    color_type: ["Color", "Type"],
    origin_color: ["Origin", "Color"],
    route_od: ["Start", "End"],
    brand_route: ["Brand", "Route"],
    unclosed_entry_camera: ["Camera", "Status"],
  }[name] || ["Group", "Value"];
}

function summaryModeLabel(mode) {
  return {
    brand: "Brand",
    color: "Color",
    type: "Type",
    event: "Event",
    origin: "Country",
    brand_color: "Brand × Color",
    origin_brand: "Country × Brand",
    origin_type: "Country × Type",
    brand_type: "Brand × Type",
    camera_event: "Camera × Event",
    hour_event: "Hour × Event",
    color_type: "Color × Type",
    origin_color: "Country × Color",
    route_od: "Start × End",
    brand_route: "Brand × Route",
    unclosed_entry_camera: "Open Entry × Camera",
  }[mode] || "Current breakdown";
}

function namedSummaryRows(counts) {
  return Object.entries(counts || {}).map(([name, count]) => ({ name, count }));
}

function renderSummaryOverview(result) {
  const summary = result.summary || {};
  const cards = [
    ["Brands", namedSummaryRows(summary.brand_counts)],
    ["Colors", namedSummaryRows(summary.color_counts)],
    ["Types", namedSummaryRows(summary.type_counts)],
    ["Events", namedSummaryRows(summary.event_counts)],
    ["Countries", namedSummaryRows(summary.origin_counts)],
  ];
  summaryOverview.innerHTML = cards.map(([title, rows]) => summaryCardHtml(title, rows)).join("");
}

function summaryCardHtml(title, rows) {
  const topRows = [...rows].sort((a, b) => Number(b.count) - Number(a.count) || a.name.localeCompare(b.name)).slice(0, 5);
  const items = topRows.length
    ? topRows.map((row) => `<li>${escapeHtml(row.name)} <strong>${escapeHtml(row.count)}</strong></li>`).join("")
    : "<li>No rows</li>";
  return `<section class="summary-card"><h3>${escapeHtml(title)}</h3><ol>${items}</ol></section>`;
}

function renderSummary(rows, columns = summaryTableColumns({}), title = "Current breakdown", mode = "") {
  const nextRows = rows || [];
  const nextColumns = columns || [];
  const previousColumnKeys = currentSummaryColumns.map((column) => column.key).join("|");
  const nextColumnKeys = nextColumns.map((column) => column.key).join("|");
  if (mode !== currentSummaryMode || previousColumnKeys !== nextColumnKeys) {
    summaryFilterValues = new Set();
    summaryRowScopes = new Map();
  }
  currentSummaryRows = nextRows;
  currentSummaryColumns = nextColumns;
  currentSummaryMode = mode;
  currentSummaryTitle = title;
  pruneSummaryRowScopes();
  renderSummaryFromState(true);
}

function renderSummaryFromState(rebuildFilter) {
  const rows = currentSummaryRows || [];
  const columns = currentSummaryColumns.length ? currentSummaryColumns : [{ key: "name", label: "Group" }, { key: "count", label: "Count" }];
  if (rebuildFilter) {
    populateSummaryFilter(rows, columns);
  }
  const filteredRows = filteredSummaryRows(rows, columns);
  const total = filteredRows.reduce((sum, row) => sum + Number(row.count || 0), 0);
  summaryFilterTotal.textContent = summaryFilterValues.size
    ? `Total: ${total} (${filteredRows.length}/${rows.length})`
    : `Total: ${total} (${rows.length})`;
  clearSummaryFilterButton.disabled = summaryFilterValues.size === 0;
  renderSummaryTable(filteredRows, columns, currentSummaryTitle);
  updateSummaryComparison();
}

function populateSummaryFilter(rows, columns) {
  const availableKeys = new Set(rows.map((row) => summaryRowKey(row, columns)));
  summaryFilterValues = new Set([...summaryFilterValues].filter((key) => availableKeys.has(key)));
  summaryFilterChoices.innerHTML = "";
  if (!rows.length) {
    summaryFilterChoices.textContent = "No rows";
    summaryFilterChoices.setAttribute("aria-disabled", "true");
    return;
  }
  rows.forEach((row) => {
    const key = summaryRowKey(row, columns);
    const label = document.createElement("label");
    label.className = "summary-filter-choice";
    label.title = summaryRowLabel(row, columns);
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = key;
    checkbox.checked = summaryFilterValues.has(key);
    const labelText = document.createElement("span");
    labelText.textContent = summaryRowLabel(row, columns);
    const count = document.createElement("strong");
    count.textContent = row.count ?? 0;
    label.append(checkbox, labelText, count);
    summaryFilterChoices.appendChild(label);
  });
  summaryFilterChoices.toggleAttribute("aria-disabled", rows.length === 0);
  summaryFilterChoices.querySelectorAll("input[type='checkbox']").forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) {
        summaryFilterValues.add(input.value);
      } else {
        summaryFilterValues.delete(input.value);
      }
      renderSummaryFromState(false);
    });
  });
}

function filteredSummaryRows(rows, columns) {
  if (!summaryFilterValues.size) {
    return rows;
  }
  return rows.filter((row) => summaryFilterValues.has(summaryRowKey(row, columns)));
}

function summaryRowKey(row, columns) {
  return columns
    .filter((column) => column.key !== "count")
    .map((column) => String(row[column.key] ?? ""))
    .join("\u001f");
}

function summaryRowLabel(row, columns) {
  return columns
    .filter((column) => column.key !== "count")
    .map((column) => String(row[column.key] ?? ""))
    .filter(Boolean)
    .join(" / ") || "Row";
}

function updateSummaryComparison() {
  if (!summaryCompareOutput) {
    return;
  }
  const compared = currentSummaryRows
    .map((row) => {
      const key = summaryRowKey(row, currentSummaryColumns);
      const scope = summaryRowScopes.get(key);
      return {
        key,
        label: summaryScopedLabel(summaryRowLabel(row, currentSummaryColumns), scope),
        count: scope?.count,
        event_count: scope?.event_count,
        compare: scope?.compare,
        scope,
      };
    })
    .filter((item) => item.compare && typeof item.count === "number");

  if (!compared.length) {
    summaryCompareOutput.textContent = "กด Calc ในแต่ละแถวแล้วติ๊ก Compare เพื่อเทียบผลที่กรองแยกกัน";
    return;
  }
  if (compared.length === 1) {
    summaryCompareOutput.textContent = `เลือกอีก 1 แถวเพื่อเทียบกับ ${compared[0].label} (${compared[0].count} คัน)`;
    return;
  }

  const sorted = [...compared].sort((a, b) => Number(b.count) - Number(a.count) || a.label.localeCompare(b.label));
  const total = sorted.reduce((sum, item) => sum + Number(item.count || 0), 0);
  const top = sorted[0];
  const second = sorted[1];
  const difference = Number(top.count || 0) - Number(second.count || 0);
  const comparisonText = difference === 0
    ? `${top.label} เท่ากับ ${second.label} ที่ ${top.count} คัน`
    : `${top.label} มากกว่า ${second.label} ${difference} คัน`;
  const selectedText = sorted.map((item) => `${item.label}: ${item.count}`).join(" | ");
  summaryCompareOutput.textContent = `Compare ${sorted.length} rows | รวม ${total} คัน | ${comparisonText} | ${selectedText}`;
}

function summaryScopedLabel(label, scope) {
  const parts = [];
  if (scope?.date) {
    parts.push(scope.date);
  }
  if (scope?.cctv_id) {
    parts.push(scope.cctv_id);
  }
  if (scope?.color) {
    parts.push(scope.color);
  }
  if (scope?.start_time && scope?.end_time) {
    parts.push(`${scope.start_time}-${scope.end_time}`);
  }
  return parts.length ? `${label} (${parts.join(", ")})` : label;
}

function renderSummaryTable(rows, columns, title) {
  summaryTitle.textContent = title;
  summaryHead.innerHTML = `${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}<th>Date</th><th>CCTV</th><th>Color</th><th>Start</th><th>End</th><th>Calc</th><th>Scoped</th><th>Compare</th>`;
  summaryRows.innerHTML = "";
  if (!rows.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="${columns.length + 8}">No rows</td>`;
    summaryRows.appendChild(row);
    return;
  }

  [...rows]
    .sort((a, b) => Number(b.count) - Number(a.count) || String(a.left || a.name || a.brand || "").localeCompare(String(b.left || b.name || b.brand || "")))
    .forEach((item) => {
    const row = document.createElement("tr");
    columns.forEach((column) => {
      const cell = document.createElement("td");
      cell.textContent = item[column.key] ?? "";
      row.appendChild(cell);
    });
    const key = summaryRowKey(item, currentSummaryColumns);
    const scope = ensureSummaryRowScope(key);
    row.appendChild(summaryRowControlCell(createSummaryScopeSelect(key, "date", summaryMetadata.dates, "เดิม", scope.date)));
    row.appendChild(summaryRowControlCell(createSummaryScopeSelect(key, "cctv_id", summaryMetadata.cctv_ids, "เดิม", scope.cctv_id)));
    row.appendChild(summaryRowControlCell(createSummaryScopeSelect(key, "color", summaryMetadata.colors, "ทุกสี", summaryRowDisplayColor(item, currentSummaryMode, scope))));
    row.appendChild(summaryRowControlCell(createSummaryScopeTimeInput(key, "start_time", scope.start_time)));
    row.appendChild(summaryRowControlCell(createSummaryScopeTimeInput(key, "end_time", scope.end_time)));
    const actionCell = document.createElement("td");
    const actionButton = document.createElement("button");
    actionButton.type = "button";
    actionButton.className = "secondary compact summary-row-button";
    actionButton.dataset.summaryRowCalc = key;
    actionButton.disabled = !summaryRowActionSupported(currentSummaryMode);
    actionButton.textContent = scope.loading ? "..." : "Calc";
    actionCell.appendChild(actionButton);
    row.appendChild(actionCell);

    const resultCell = document.createElement("td");
    resultCell.className = "summary-row-result";
    if (scope.error) {
      resultCell.classList.add("error");
    }
    resultCell.textContent = summaryRowResultText(scope);
    row.appendChild(resultCell);

    const compareCell = document.createElement("td");
    const compareLabel = document.createElement("label");
    compareLabel.className = "summary-row-compare-choice";
    const compareInput = document.createElement("input");
    compareInput.type = "checkbox";
    compareInput.className = "summary-row-compare";
    compareInput.dataset.summaryRowKey = key;
    compareInput.checked = Boolean(scope.compare);
    compareInput.disabled = typeof scope.count !== "number" || scope.loading || Boolean(scope.error);
    const compareText = document.createElement("span");
    compareText.textContent = "Compare";
    compareLabel.append(compareInput, compareText);
    compareCell.appendChild(compareLabel);
    row.appendChild(compareCell);
    summaryRows.appendChild(row);
  });
}

function summaryRowControlCell(control) {
  const cell = document.createElement("td");
  cell.className = "summary-row-scope-cell";
  cell.appendChild(control);
  return cell;
}

function createSummaryScopeSelect(key, field, values, emptyLabel, value) {
  const select = document.createElement("select");
  select.className = "summary-row-scope-control summary-row-scope-select";
  select.dataset.summaryRowKey = key;
  select.dataset.summaryScopeField = field;
  populateSelect(select, values || [], emptyLabel);
  select.value = value || "";
  return select;
}

function summaryRowDisplayColor(item, mode, scope) {
  if (scope.color) {
    return scope.color;
  }
  if (mode === "color") {
    return item.name || "";
  }
  if (mode === "brand_color") {
    return item.color || "";
  }
  if (mode === "color_type") {
    return item.left || "";
  }
  if (mode === "origin_color") {
    return item.right || "";
  }
  return "";
}

function createSummaryScopeTimeInput(key, field, value) {
  const input = document.createElement("input");
  input.type = "time";
  input.step = "1";
  input.className = "summary-row-scope-control summary-row-scope-time";
  input.dataset.summaryRowKey = key;
  input.dataset.summaryScopeField = field;
  input.value = value || "";
  return input;
}

function summaryRowResultText(scope) {
  if (scope.loading) {
    return "Calculating...";
  }
  if (scope.error) {
    return scope.error;
  }
  if (typeof scope.count === "number") {
    return `${scope.count} คัน (${scope.event_count || 0} detections)`;
  }
  if (!summaryRowActionSupported(currentSummaryMode)) {
    return "ยังไม่รองรับ";
  }
  return "-";
}

function summaryRowActionSupported(mode) {
  return new Set([
    "brand",
    "color",
    "type",
    "event",
    "origin",
    "brand_color",
    "origin_brand",
    "origin_type",
    "brand_type",
    "camera_event",
    "hour_event",
    "color_type",
    "origin_color",
    "unclosed_entry_camera",
  ]).has(mode);
}

function defaultSummaryRowScope() {
  const query = latestResult?.query || {};
  const scope = selectedSummaryScope();
  const hasScopedTime = scope.start_time && scope.end_time && !scope.invalidTime;
  return {
    date: scope.date || query.date || "",
    cctv_id: scope.cctv_id || query.cctv_id || "",
    color: "",
    start_time: hasScopedTime ? scope.start_time : query.start_time || "",
    end_time: hasScopedTime ? scope.end_time : query.end_time || "",
    loading: false,
    compare: false,
  };
}

function ensureSummaryRowScope(key) {
  if (!summaryRowScopes.has(key)) {
    summaryRowScopes.set(key, defaultSummaryRowScope());
  }
  return summaryRowScopes.get(key);
}

function pruneSummaryRowScopes() {
  const availableKeys = new Set(currentSummaryRows.map((row) => summaryRowKey(row, currentSummaryColumns)));
  summaryRowScopes = new Map([...summaryRowScopes].filter(([key]) => availableKeys.has(key)));
}

function updateSummaryRowScope(key, field, value) {
  const scope = { ...ensureSummaryRowScope(key), [field]: value };
  delete scope.count;
  delete scope.event_count;
  delete scope.answer;
  delete scope.question;
  scope.error = "";
  scope.loading = false;
  scope.compare = false;
  summaryRowScopes.set(key, scope);
  renderSummaryFromState(false);
}

function updateSummaryRowCompare(key, checked) {
  const scope = { ...ensureSummaryRowScope(key), compare: checked };
  summaryRowScopes.set(key, scope);
  updateSummaryComparison();
}

async function calculateSummaryRow(key) {
  const item = currentSummaryRows.find((row) => summaryRowKey(row, currentSummaryColumns) === key);
  if (!item) {
    return;
  }
  const scope = { ...ensureSummaryRowScope(key), loading: false };
  const scopeError = summaryScopeError(scope, "แถว Summary");
  if (scopeError) {
    summaryRowScopes.set(key, { ...scope, error: scopeError, compare: false });
    renderSummaryFromState(false);
    return;
  }
  const question = buildSummaryRowQuestion(item, currentSummaryMode, scope, { silent: true });
  if (!question) {
    summaryRowScopes.set(key, { ...scope, error: "แถวนี้ยังใช้คำนวณต่อไม่ได้", compare: false });
    renderSummaryFromState(false);
    return;
  }

  summaryRowScopes.set(key, { ...scope, loading: true, error: "" });
  renderSummaryFromState(false);
  statusPill.textContent = "Summary";
  try {
    const response = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, use_llm: false }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Summary row query failed");
    }
    summaryRowScopes.set(key, {
      ...scope,
      loading: false,
      error: "",
      count: Number(payload.count ?? 0),
      event_count: Number(payload.event_count ?? 0),
      answer: payload.answer || "",
      question,
    });
    statusPill.textContent = "Ready";
  } catch (error) {
    summaryRowScopes.set(key, { ...scope, loading: false, error: error.message || "Query failed", compare: false });
    statusPill.textContent = "Error";
  } finally {
    renderSummaryFromState(false);
  }
}

function runSummaryRowQuestion(index) {
  const item = currentSummaryRows[index];
  if (!item) {
    return;
  }
  const question = buildSummaryRowQuestion(item, currentSummaryMode);
  if (!question) {
    return;
  }
  submitQuestionOnly = true;
  pendingSummaryMode = null;
  questionInput.value = question;
  form.requestSubmit();
}

function buildSummaryRowQuestion(item, mode, scope = selectedSummaryScope(), options = {}) {
  const error = summaryScopeError(scope, "Summary");
  if (error) {
    if (!options.silent) {
      renderError(error);
    }
    return "";
  }

  const query = latestResult?.query || {};
  const parts = [];
  const date = scope.date || query.date;
  const cctvId = scope.cctv_id || query.cctv_id;
  const startTime = scope.start_time || query.start_time;
  const endTime = scope.end_time || query.end_time;
  if (date) {
    parts.push(`date ${date}`);
  }
  if (cctvId) {
    parts.push(cctvId);
  }
  if (startTime && endTime) {
    parts.push(`from ${startTime} to ${endTime}`);
  }
  const rowParts = summaryRowQuestionParts(item, mode, Boolean(startTime && endTime), scope);
  if (!rowParts.length) {
    if (!options.silent) {
      renderError("Summary row นี้ยังใช้เป็น filter ต่อไม่ได้");
    }
    return "";
  }
  parts.push(...baseSummaryContextParts(query, mode, scope));
  if (scope.color && !summaryModeHasRowColor(mode)) {
    parts.push(`color ${scope.color}`);
  }
  parts.push(...rowParts);
  parts.push("vehicles");
  return parts.filter(Boolean).join(" ");
}

function summaryScopeError(scope, label) {
  const startTime = scope.start_time || "";
  const endTime = scope.end_time || "";
  if (scope.invalidTime || Boolean(startTime) !== Boolean(endTime)) {
    return `กรุณาเลือกเวลาเริ่มและเวลาสิ้นสุดใน ${label} ให้ครบ หรือปล่อยว่างทั้งคู่`;
  }
  return "";
}

function selectedSummaryScope() {
  const startTime = summaryScopeStart.value;
  const endTime = summaryScopeEnd.value;
  return {
    date: summaryScopeDate.value,
    cctv_id: summaryScopeCctv.value,
    start_time: startTime,
    end_time: endTime,
    invalidTime: Boolean(startTime) !== Boolean(endTime),
  };
}

function syncSummaryScopeFromQuery(query) {
  summaryScopeDate.value = query.date || "";
  summaryScopeCctv.value = query.cctv_id || "";
  summaryScopeStart.value = query.start_time || "";
  summaryScopeEnd.value = query.end_time || "";
}

function baseSummaryContextParts(query, mode, scope = {}) {
  const parts = [];
  const queryBrands = Array.isArray(query.brands) && query.brands.length ? query.brands : (query.brand ? [query.brand] : []);
  if (queryBrands.length && !["brand", "brand_color", "origin_brand", "brand_type", "brand_route"].includes(mode)) {
    parts.push(`brand ${queryBrands.join(" and ")}`);
  }
  const queryColors = Array.isArray(query.colors) && query.colors.length ? query.colors : (query.color ? [query.color] : []);
  if (!scope.color && queryColors.length && !["color", "brand_color", "color_type", "origin_color"].includes(mode)) {
    parts.push(`color ${queryColors.join(" and ")}`);
  }
  if (query.vehicle_type && !["type", "origin_type", "brand_type", "color_type"].includes(mode)) {
    parts.push(`type ${query.vehicle_type}`);
  }
  if (Array.isArray(query.brand_origins) && query.brand_origins.length && !["origin", "origin_brand", "origin_type", "origin_color"].includes(mode)) {
    parts.push(`origin ${query.brand_origins.join(" and ")}`);
  }
  if (query.event && !["event", "camera_event", "hour_event"].includes(mode)) {
    parts.push(`event ${query.event}`);
  }
  return parts;
}

function summaryModeHasRowColor(mode) {
  return ["color", "brand_color", "color_type", "origin_color"].includes(mode);
}

function summaryRowQuestionParts(item, mode, hasScopedTime = false, scope = {}) {
  const color = scope.color || "";
  switch (mode) {
    case "brand":
      return [`brand ${item.name}`];
    case "color":
      return [`color ${color || item.name}`];
    case "type":
      return [`type ${item.name}`];
    case "event":
      return [`event ${item.name}`];
    case "origin":
      return [`origin ${item.name}`];
    case "brand_color":
      return [`brand ${item.brand}`, `color ${color || item.color}`];
    case "origin_brand":
      return [`origin ${item.left}`, `brand ${item.right}`];
    case "origin_type":
      return [`origin ${item.left}`, `type ${item.right}`];
    case "brand_type":
      return [`brand ${item.left}`, `type ${item.right}`];
    case "camera_event":
      return [item.left, `event ${item.right}`];
    case "hour_event":
      return [hasScopedTime ? "" : `from ${summaryHourStart(item.left)} to ${summaryHourEnd(item.left)}`, `event ${item.right}`].filter(Boolean);
    case "color_type":
      return [`color ${color || item.left}`, `type ${item.right}`];
    case "origin_color":
      return [`origin ${item.left}`, `color ${color || item.right}`];
    case "unclosed_entry_camera":
      return [item.left, "entry without exit"];
    default:
      return [];
  }
}

function summaryHourStart(label) {
  const hour = String(label || "").match(/\d{1,2}/)?.[0] || "00";
  return `${hour.padStart(2, "0")}:00:00`;
}

function summaryHourEnd(label) {
  const hour = String(label || "").match(/\d{1,2}/)?.[0] || "00";
  return `${hour.padStart(2, "0")}:59:59`;
}

function resetSummaryFilter() {
  currentSummaryRows = [];
  currentSummaryColumns = [];
  currentSummaryMode = "";
  currentSummaryTitle = "Current breakdown";
  summaryFilterValues = new Set();
  summaryRowScopes = new Map();
  summaryFilterChoices.innerHTML = "";
  summaryFilterChoices.setAttribute("aria-disabled", "true");
  clearSummaryFilterButton.disabled = true;
  summaryFilterTotal.textContent = "Total: 0";
  updateSummaryComparison();
}

function renderRoutes(routes) {
  routeList.innerHTML = "";
  if (!routes.length) {
    routeList.textContent = "No routes";
    return;
  }

  routes.forEach((route, index) => {
    const item = document.createElement("article");
    item.className = "route-item";
    const label = `${route.brand} ${route.color} ${route.type}`;
    item.innerHTML = `
      <div class="route-title">
        <span>${index + 1}. ${escapeHtml(label)}</span>
        <span class="route-meta">${escapeHtml(route.start_time)}-${escapeHtml(route.end_time)}</span>
      </div>
      <div class="route-path">${escapeHtml((route.path || []).join(" -> "))}</div>
      <div class="route-meta">${route.event_count || 0} detections</div>
    `;
    routeList.appendChild(item);
  });
}

function renderBatchRows(rows) {
  batchRows.innerHTML = "";
  if (!rows.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="3">No rows</td>';
    batchRows.appendChild(row);
    return;
  }

  rows.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(item.question_id)}</td>
      <td>${escapeHtml(item.answer)}</td>
      <td><code>${escapeHtml(item.csv_answer)}</code></td>
    `;
    batchRows.appendChild(row);
  });
}

function renderNotice(message) {
  latestResult = null;
  latestBatch = null;
  latestSql = null;
  answerOutput.classList.remove("error");
  answerOutput.textContent = message;
  jsonOutput.textContent = "{}";
  csvOutput.textContent = "Question ID,Answer";
  csvAnswerToolbar.hidden = true;
  csvAnswerMode.innerHTML = "";
  csvAnswerMeta.textContent = "";
  exportCsvButton.disabled = true;
  countMetric.textContent = "-";
  eventMetric.textContent = "-";
  routeMetric.textContent = "-";
  followUpActions.hidden = true;
  followUpActions.innerHTML = "";
  summaryRows.innerHTML = "";
  summaryOverview.innerHTML = "";
  summaryTitle.textContent = "Current breakdown";
  resetSummaryFilter();
  routeList.textContent = "";
  batchRows.innerHTML = "";
  sqlTableSelect.innerHTML = "";
  sqlTableHead.innerHTML = "";
  sqlRows.innerHTML = "";
  sqlOutput.textContent = "";
  sqlMeta.textContent = "No SQL table";
  exportSqlCsvButton.disabled = true;
}

function renderError(message) {
  latestResult = null;
  latestBatch = null;
  latestSql = null;
  answerOutput.classList.add("error");
  answerOutput.textContent = message;
  jsonOutput.textContent = "{}";
  csvOutput.textContent = "Question ID,Answer";
  csvAnswerToolbar.hidden = true;
  csvAnswerMode.innerHTML = "";
  csvAnswerMeta.textContent = "";
  exportCsvButton.disabled = true;
  countMetric.textContent = "-";
  eventMetric.textContent = "-";
  routeMetric.textContent = "-";
  followUpActions.hidden = true;
  followUpActions.innerHTML = "";
  summaryRows.innerHTML = "";
  summaryOverview.innerHTML = "";
  summaryTitle.textContent = "Current breakdown";
  resetSummaryFilter();
  routeList.textContent = "";
  batchRows.innerHTML = "";
  sqlTableSelect.innerHTML = "";
  sqlTableHead.innerHTML = "";
  sqlRows.innerHTML = "";
  sqlOutput.textContent = "";
  sqlMeta.textContent = "No SQL table";
  exportSqlCsvButton.disabled = true;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function downloadTextFile(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    const payload = await response.json();
    llmToggle.checked = Boolean(payload.llm_enabled);
    statusPill.textContent = llmToggle.checked ? "LLM" : "Local";
    statusPill.title = payload.llm_model ? `${payload.llm_model} @ ${payload.llm_base_url}` : "";
  } catch (error) {
    statusPill.textContent = "Local";
  }
}

window.addEventListener("load", async () => {
  await loadHealth();
  form.requestSubmit();
});
