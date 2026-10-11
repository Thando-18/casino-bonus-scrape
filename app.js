const DATA_URL = "data/bonuses.json";
const STALE_AFTER_DAYS = 7;
const fields = [
  ["casino_name", "Casino"],
  ["welcome_bonus", "Welcome bonus"],
  ["wagering_requirement", "Wagering multiplier"],
  ["minimum_deposit", "Minimum deposit"],
];

let casinos = [];
let sort = { key: null, dir: 1 };

function display(key, value) {
  if (value === null || value === undefined || value === "") {
    return key === "wagering_requirement" ? "Not stated / varies" : "Not stated";
  }
  return key === "wagering_requirement" ? `${value}x` : String(value);
}

function textCell(key, label, value) {
  const td = document.createElement("td");
  td.dataset.label = label;
  td.textContent = display(key, value);
  return td;
}

function sortValue(key, value) {
  if (key === "wagering_requirement") return typeof value === "number" ? value : Infinity;
  if (key === "minimum_deposit") {
    const n = parseFloat(String(value ?? "").replace(/[^\d.]/g, ""));
    return Number.isNaN(n) ? Infinity : n;
  }
  return String(value ?? "").toLowerCase();
}

function render(data) {
  const tbody = document.querySelector("#bonus-rows");
  tbody.replaceChildren();
  const rows = [...casinos];
  if (sort.key) {
    rows.sort((a, b) => {
      const x = sortValue(sort.key, a[sort.key]);
      const y = sortValue(sort.key, b[sort.key]);
      return (x < y ? -1 : x > y ? 1 : 0) * sort.dir;
    });
  }
  rows.forEach((casino) => {
    const tr = document.createElement("tr");
    fields.forEach(([key, label]) => tr.appendChild(textCell(key, label, casino[key])));
    const source = document.createElement("td");
    source.dataset.label = "Source";
    const link = document.createElement("a");
    link.href = casino.source_url || data.source_page;
    link.textContent = "View source";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    source.appendChild(link);
    tr.appendChild(source);
    tbody.appendChild(tr);
  });
  document.querySelectorAll("th[data-key]").forEach((th) => {
    th.setAttribute("aria-sort", th.dataset.key === sort.key ? (sort.dir === 1 ? "ascending" : "descending") : "none");
  });
}

function wireSorting(data) {
  document.querySelectorAll("th[data-key]").forEach((th) => {
    const activate = () => {
      sort = { key: th.dataset.key, dir: sort.key === th.dataset.key ? -sort.dir : 1 };
      render(data);
    };
    th.addEventListener("click", activate);
    th.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); activate(); }
    });
  });
}

async function loadBonuses() {
  const status = document.querySelector("#status");
  const table = document.querySelector("#bonus-table");
  const stale = document.querySelector("#stale");
  try {
    const response = await fetch(DATA_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`JSON request failed (${response.status})`);
    const data = await response.json();
    casinos = Array.isArray(data.casinos) ? data.casinos : [];
    document.querySelector("#record-count").textContent = `${casinos.length} record${casinos.length === 1 ? "" : "s"}`;
    const updated = document.querySelector("#updated");
    if (data.scraped_at) {
      const when = new Date(data.scraped_at);
      updated.textContent = `Last generated: ${when.toLocaleString()}`;
      const ageDays = (Date.now() - when.getTime()) / 86400000;
      if (ageDays > STALE_AFTER_DAYS) {
        stale.hidden = false;
        stale.textContent = `This data is ${Math.floor(ageDays)} days old and may be out of date. Check the operator's site for current terms.`;
      }
    } else {
      updated.textContent = "No successful scrape has been run yet";
    }
    if (!casinos.length) {
      status.textContent = "No extracted records yet. Run the Python scraper after configuring your API key and verifying that the source permits scraping.";
      return;
    }
    wireSorting(data);
    render(data);
    status.hidden = true;
    table.hidden = false;
  } catch (error) {
    status.classList.add("error");
    status.textContent = `Could not load bonus data: ${error.message}. Serve the project over HTTP (e.g. python -m http.server) and check the JSON path.`;
  }
}
loadBonuses();
