/* Original synthetic teaching illustration. No research data or third-party code. */
(() => {
  "use strict";
  const data = window.SYNTHETIC_MUSIC;
  if (!data || data.synthetic !== true || !Array.isArray(data.nodes)) return;
  const $ = id => document.getElementById(id);
  const NS = "http://www.w3.org/2000/svg";
  const graph = $("graph");
  const nodes = data.nodes;
  const byId = new Map(nodes.map(node => [node.id, node]));
  const colors = ["#80619c", "#387f81", "#95652e"];
  let selected = nodes[0].id;
  const cosine = (a, b) => {
    const dot = a.reduce((sum, x, index) => sum + x * b[index], 0);
    const norm = Math.sqrt(a.reduce((s, x) => s + x * x, 0) * b.reduce((s, x) => s + x * x, 0));
    return Math.max(-1, Math.min(1, dot / norm));
  };
  const similarity = (a, b, w) => w * cosine(a.surface, b.surface) + (1 - w) * cosine(a.pattern, b.pattern);
  const svgElement = (tag, attrs) => {
    const element = document.createElementNS(NS, tag);
    for (const [name, value] of Object.entries(attrs)) element.setAttribute(name, String(value));
    return element;
  };
  const edgeLayer = svgElement("g", {"aria-hidden": "true"});
  const nodeLayer = svgElement("g", {});
  graph.append(edgeLayer, nodeLayer);
  for (const node of nodes) {
    const option = document.createElement("option");
    option.value = node.id;
    option.textContent = node.id;
    $("selected-node").append(option);
    const group = svgElement("g", {class: "graph-node", tabindex: 0, role: "button", "aria-label": `Inspect synthetic node ${node.id}`, "data-node": node.id});
    const circle = svgElement("circle", {cx: node.x, cy: node.y, r: 18, fill: colors[node.surface_group]});
    const label = svgElement("text", {x: node.x, y: node.y + 4, "text-anchor": "middle", fill: "white", "font-family": "Arial,sans-serif", "font-size": 11, "font-weight": 700});
    label.textContent = node.id;
    group.append(circle, label);
    group.addEventListener("click", () => select(node.id));
    group.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select(node.id);
      }
    });
    nodeLayer.append(group);
  }
  const settings = () => ({w: Number($("weight").value) / 100, k: Number($("neighbors").value), t: Number($("threshold").value) / 100});
  function select(id) {
    selected = id;
    $("selected-node").value = id;
    render();
  }
  function render() {
    const {w, k, t} = settings();
    $("weight-value").value = `${Math.round(w * 100)}%`;
    $("weight").setAttribute("aria-valuetext", `${Math.round(w * 100)} percent surface; ${Math.round((1 - w) * 100)} percent pattern`);
    $("neighbors-value").value = String(k);
    $("threshold-value").value = t.toFixed(2);
    const edges = new Map();
    for (const node of nodes) {
      const neighbors = nodes.filter(other => other.id !== node.id)
        .map(other => ({id: other.id, score: similarity(node, other, w)}))
        .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
      for (const other of neighbors.slice(0, k)) {
        if (other.score >= t) {
          const pair = [node.id, other.id].sort();
          edges.set(pair.join(":"), {a: pair[0], b: pair[1], score: other.score});
        }
      }
    }
    edgeLayer.replaceChildren();
    const connected = new Set();
    const selectedNeighbors = [];
    for (const edge of edges.values()) {
      const a = byId.get(edge.a), b = byId.get(edge.b);
      const active = edge.a === selected || edge.b === selected;
      edgeLayer.append(svgElement("line", {x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: active ? "graph-edge selected" : "graph-edge"}));
      connected.add(edge.a); connected.add(edge.b);
      if (active) selectedNeighbors.push({id: edge.a === selected ? edge.b : edge.a, score: edge.score});
    }
    for (const group of nodeLayer.children) {
      const active = group.getAttribute("data-node") === selected;
      group.classList.toggle("selected", active);
      group.setAttribute("aria-pressed", String(active));
    }
    $("graph-summary").textContent = `${nodes.length} invented nodes · ${edges.size} toy edges · ${nodes.length - connected.size} isolated nodes`;
    $("selected-title").textContent = `${selected} neighborhood`;
    const chosen = byId.get(selected);
    $("node-explanation").textContent = `Assigned surface group ${chosen.surface_group + 1}, pattern group ${chosen.pattern_group + 1}. Graph degree can exceed k because edges include incoming choices.`;
    $("neighbor-list").replaceChildren();
    selectedNeighbors.sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
    if (!selectedNeighbors.length) {
      const empty = document.createElement("li");
      empty.textContent = "No edges at these settings.";
      $("neighbor-list").append(empty);
    }
    for (const neighbor of selectedNeighbors) {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = neighbor.id;
      button.setAttribute("aria-label", `Inspect synthetic node ${neighbor.id}`);
      button.addEventListener("click", () => select(neighbor.id));
      const value = document.createElement("span");
      value.textContent = neighbor.score.toFixed(3);
      item.append(button, value);
      $("neighbor-list").append(item);
    }
  }
  for (const id of ["weight", "neighbors", "threshold"]) $(id).addEventListener("input", render);
  $("selected-node").addEventListener("change", event => select(event.target.value));
  $("reset").addEventListener("click", () => {
    $("weight").value = String(data.default.surface_weight * 100);
    $("neighbors").value = String(data.default.k);
    $("threshold").value = String(data.default.threshold * 100);
    select(nodes[0].id);
  });
  render();
})();
