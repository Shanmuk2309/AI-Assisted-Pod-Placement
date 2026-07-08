import { useState, useEffect } from "react";
import {
  recommendBaseline,
  recommendML,
  recommendDataset,
  listScenarios,
} from "../api";
import {
  createDefaultScenario,
  createDefaultNode,
  buildLatencyMatrix,
  buildRandomLatencyMatrix,
  buildScenarioPayload,
  ZONES,
} from "../utils/scenario";

export default function ScenarioForm() {
  const [form, setForm] = useState(createDefaultScenario);
  const [savedScenarios, setSavedScenarios] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listScenarios()
      .then(setSavedScenarios)
      .catch(() => setSavedScenarios([]));
  }, []);

  function loadScenario(scenario) {
    setForm({
      scenario_id: scenario.scenario_id,
      difficulty: scenario.difficulty,
      nodes: scenario.nodes,
      latency_matrix: scenario.latency_matrix,
      workload: scenario.workload,
    });
    setResult(null);
    setError("");
  }

  function updateNode(index, field, value) {
    setForm((prev) => {
      const nodes = [...prev.nodes];
      nodes[index] = { ...nodes[index], [field]: value };
      return { ...prev, nodes, latency_matrix: buildLatencyMatrix(nodes) };
    });
  }

  function addNode() {
    setForm((prev) => {
      const nodes = [...prev.nodes, createDefaultNode(prev.nodes.length)];
      return { ...prev, nodes, latency_matrix: buildLatencyMatrix(nodes) };
    });
  }

  function removeNode(index) {
    if (form.nodes.length <= 2) return;
    setForm((prev) => {
      const nodes = prev.nodes.filter((_, i) => i !== index);
      return { ...prev, nodes, latency_matrix: buildLatencyMatrix(nodes) };
    });
  }

  function updateLatency(from, to, value) {
    setForm((prev) => ({
      ...prev,
      latency_matrix: {
        ...prev.latency_matrix,
        [from]: { ...prev.latency_matrix[from], [to]: Number(value) },
      },
    }));
  }

  function updateWorkload(pod, field, value) {
    setForm((prev) => ({
      ...prev,
      workload: {
        ...prev.workload,
        [pod]: { ...prev.workload[pod], [field]: Number(value) },
      },
    }));
  }

  function regenerateLatency() {
    setForm((prev) => ({
      ...prev,
      latency_matrix: buildRandomLatencyMatrix(prev.nodes),
    }));
  }

  function generateScenarioId() {
    setForm((prev) => ({
      ...prev,
      scenario_id: crypto.randomUUID(),
    }));
  }

  async function handleRecommend(method) {
    setLoading(method);
    setError("");
    setResult(null);
    try {
      const scenario = buildScenarioPayload(form);
      let data;

      if (method === "ml") {
        data = await recommendML(scenario);
        data.scenario = scenario;
      } else if (method === "dataset") {
        data = await recommendDataset(scenario);
      } else {
        data = await recommendBaseline(scenario);
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(null);
    }
  }

  const nodeNames = form.nodes.map((n) => n.name);
  const displayScenario = result?.scenario || form;

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="section-title">Custom Scenario Placement</h2>
        <p className="text-sm text-slate-400 mt-1">
          Define a cluster scenario and get optimal CU/DU pod placement recommendations
        </p>
      </div>

      {/* Load saved scenario */}
      {savedScenarios.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-surface-700/40 border border-surface-600/30">
          <label className="field-label">Load Generated Scenario</label>
          <select
            defaultValue=""
            onChange={(e) => {
              const selected = savedScenarios.find(
                (s) => s.scenario_id === e.target.value
              );
              if (selected) loadScenario(selected);
            }}
            className="w-full"
          >
            <option value="" disabled>
              Select a scenario from database ({savedScenarios.length} available)
            </option>
            {savedScenarios.map((s) => (
              <option key={s.scenario_id} value={s.scenario_id}>
                {s.difficulty} — {s.scenario_id.slice(0, 8)}… ({s.nodes.length} nodes)
              </option>
            ))}
          </select>
          <p className="text-xs text-slate-500 mt-1.5">
            Required for Dataset lookup — only generated scenarios exist in the dataset
          </p>
        </div>
      )}

      {/* Scenario ID */}
      <div className="mb-6">
        <label className="field-label">Scenario ID</label>

        <div className="flex gap-3">

          <input
            value={form.scenario_id}
            onChange={(e) =>
              setForm((p) => ({
                ...p,
                scenario_id: e.target.value,
              }))
            }
            className="flex-1 font-mono text-xs"
            placeholder="Enter Scenario ID or generate one"
          />

          <button
            type="button"
            onClick={generateScenarioId}
            className="btn-primary whitespace-nowrap"
          >
            🎲 Generate
          </button>

        </div>

        <p className="text-xs text-slate-500 mt-2">
          Enter your own Scenario ID or generate a UUID automatically.
        </p>
      </div>

      {/* Difficulty */}
      <div className="mb-6">
        <label className="field-label">Difficulty</label>
        <select
          value={form.difficulty}
          onChange={(e) => setForm((p) => ({ ...p, difficulty: e.target.value }))}
          className="w-full sm:w-48"
        >
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>

      {/* Nodes */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <label className="field-label mb-0">Cluster Nodes</label>
          <button onClick={addNode} className="btn-secondary text-xs py-1.5 px-3">
            + Add Node
          </button>
        </div>

        <div className="space-y-3">
          {form.nodes.map((node, i) => (
            <div
              key={i}
              className="p-4 rounded-xl bg-surface-700/40 border border-surface-600/30"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-300">Node {i + 1}</span>
                {form.nodes.length > 2 && (
                  <button
                    onClick={() => removeNode(i)}
                    className="text-xs text-red-400 hover:text-red-300 transition-colors"
                  >
                    Remove
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                <Field label="Name" value={node.name} onChange={(v) => updateNode(i, "name", v)} />
                <div>
                  <label className="field-label">Zone</label>
                  <select
                    value={node.zone}
                    onChange={(e) => updateNode(i, "zone", e.target.value)}
                    className="w-full"
                  >
                    {ZONES.map((z) => (
                      <option key={z} value={z}>{z}</option>
                    ))}
                  </select>
                </div>
                <Field label="Load" type="number" step="0.01" value={node.load} onChange={(v) => updateNode(i, "load", v)} />
                <Field label="CPU Cap" type="number" value={node.cpu_capacity} onChange={(v) => updateNode(i, "cpu_capacity", v)} />
                <Field label="CPU Used" type="number" value={node.cpu_used} onChange={(v) => updateNode(i, "cpu_used", v)} />
                <Field label="Mem Cap" type="number" value={node.mem_capacity} onChange={(v) => updateNode(i, "mem_capacity", v)} />
                <Field label="Mem Used" type="number" value={node.mem_used} onChange={(v) => updateNode(i, "mem_used", v)} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Workload */}
      <div className="mb-6">
        <label className="field-label">Workload Requirements</label>
        <div className="grid sm:grid-cols-2 gap-4">
          <WorkloadCard
            title="CU Pod (Central Unit)"
            color="violet"
            cpu={form.workload.cu.cpu_req}
            mem={form.workload.cu.mem_req}
            onCpu={(v) => updateWorkload("cu", "cpu_req", v)}
            onMem={(v) => updateWorkload("cu", "mem_req", v)}
          />
          <WorkloadCard
            title="DU Pod (Distributed Unit)"
            color="emerald"
            cpu={form.workload.du.cpu_req}
            mem={form.workload.du.mem_req}
            onCpu={(v) => updateWorkload("du", "cpu_req", v)}
            onMem={(v) => updateWorkload("du", "mem_req", v)}
          />
        </div>
        <div className="mt-3 max-w-xs">
          <label className="field-label">Latency Budget (ms)</label>
          <input
            type="number"
            min={1}
            value={form.workload.latency_budget}
            onChange={(e) =>
              setForm((p) => ({
                ...p,
                workload: { ...p.workload, latency_budget: Number(e.target.value) },
              }))
            }
            className="w-full"
          />
        </div>
      </div>

      {/* Latency Matrix */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <label className="field-label mb-0">Latency Matrix (ms)</label>
          <button onClick={regenerateLatency} className="btn-secondary text-xs py-1.5 px-3">
            Auto-fill from Zones
          </button>
        </div>
        <div className="overflow-x-auto rounded-xl border border-surface-600/30">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-700/60">
                <th className="p-2 text-left text-slate-500 font-medium" />
                {nodeNames.map((n) => (
                  <th key={n} className="p-2 text-center text-slate-400 font-medium text-xs">{n}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {nodeNames.map((from) => (
                <tr key={from} className="border-t border-surface-600/20">
                  <td className="p-2 text-slate-400 font-medium text-xs">{from}</td>
                  {nodeNames.map((to) => (
                    <td key={to} className="p-1">
                      <input
                        type="number"
                        min={1}
                        value={form.latency_matrix[from]?.[to] ?? 1}
                        onChange={(e) => updateLatency(from, to, e.target.value)}
                        className="w-16 text-center text-xs py-1.5"
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={() => handleRecommend("baseline")}
          disabled={loading !== null}
          className="btn-baseline flex-1"
        >
          {loading === "baseline" ? <Spinner /> : <BaselineIcon />}
          Baseline
        </button>
        <button
          onClick={() => handleRecommend("ml")}
          disabled={loading !== null}
          className="btn-ml flex-1"
        >
          {loading === "ml" ? <Spinner /> : <MLIcon />}
          ML Model
        </button>
        <button
          onClick={() => handleRecommend("dataset")}
          disabled={loading !== null}
          className="btn-dataset flex-1"
        >
          {loading === "dataset" ? <Spinner /> : <DatasetIcon />}
          From Dataset
        </button>
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {result && (
        <ResultCard
          result={result}
          scenario={displayScenario}
        />
      )}
    </div>
  );
}

function Field({ label, value, onChange, type = "text", step }) {
  return (
    <div>
      <label className="field-label">{label}</label>
      <input
        type={type}
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full"
      />
    </div>
  );
}

function WorkloadCard({ title, color, cpu, mem, onCpu, onMem }) {
  const borderColor = color === "violet" ? "border-violet-500/20" : "border-emerald-500/20";
  const bgColor = color === "violet" ? "bg-violet-500/5" : "bg-emerald-500/5";
  const dotColor = color === "violet" ? "bg-violet-400" : "bg-emerald-400";

  return (
    <div className={`p-4 rounded-xl ${bgColor} border ${borderColor}`}>
      <div className="flex items-center gap-2 mb-3">
        <span className={`w-2 h-2 rounded-full ${dotColor}`} />
        <span className="text-sm font-medium text-slate-300">{title}</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="field-label">CPU Req</label>
          <input type="number" min={1} value={cpu} onChange={(e) => onCpu(e.target.value)} className="w-full" />
        </div>
        <div>
          <label className="field-label">Mem Req</label>
          <input type="number" min={1} value={mem} onChange={(e) => onMem(e.target.value)} className="w-full" />
        </div>
      </div>
    </div>
  );
}

function ResultCard({ result, scenario }) {
  const methodLabels = {
    baseline: "Baseline",
    ml: "ML Model",
    dataset: "Dataset",
  };
  const method = result.method;
  const score = result.score ?? result.predicted_score;
  const nodes = scenario?.nodes || [];
  const cuNode = nodes.find((n) => n.name === result.placement?.cu_node);
  const duNode = nodes.find((n) => n.name === result.placement?.du_node);

  const accentStyles = {
    baseline: "from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-300",
    ml: "from-violet-500/20 to-indigo-500/10 border-violet-500/30 text-violet-300",
    dataset: "from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-300",
  };

  return (
    <div className="mt-6 space-y-5">
      {/* Score + Placement */}
      <div className="p-5 rounded-2xl bg-gradient-to-br from-surface-700/80 to-surface-700/40 border border-surface-600/50 shadow-glow">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-gradient-to-br ${accentStyles[method]}`}>
              {method === "baseline" && <BaselineIcon />}
              {method === "ml" && <MLIcon />}
              {method === "dataset" && <DatasetIcon />}
            </div>
            <div>
              <h3 className="font-display font-semibold text-white">
                {methodLabels[method]} Result
              </h3>
              {method === "dataset" && result.total_placements_evaluated && (
                <p className="text-xs text-slate-500">
                  Best of {result.total_placements_evaluated} pre-computed placements
                </p>
              )}
            </div>
          </div>

          <div className={`px-5 py-3 rounded-xl border bg-gradient-to-br ${accentStyles[method]}`}>
            <p className="text-xs uppercase tracking-wider opacity-70">
              {method === "ml" ? "Predicted Score" : "Score"}
            </p>
            <p className="font-mono text-2xl font-bold text-white">
              {Number(score).toFixed(4)}
            </p>
            <p className="text-xs opacity-60">lower is better</p>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <PlacementCard label="CU Pod →" nodeName={result.placement?.cu_node} node={cuNode} accent="violet" />
          <PlacementCard label="DU Pod →" nodeName={result.placement?.du_node} node={duNode} accent="emerald" />
        </div>
      </div>

      {/* Full Scenario Details */}
      {scenario && <ScenarioDetails scenario={scenario} />}
    </div>
  );
}

function ScenarioDetails({ scenario }) {
  return (
    <div className="p-5 rounded-2xl bg-surface-700/30 border border-surface-600/40">
      <h4 className="font-display font-semibold text-white mb-4">Scenario Details</h4>

      <div className="grid sm:grid-cols-2 gap-3 text-sm">
        <DetailItem label="Scenario ID" value={scenario.scenario_id} mono />
        <DetailItem label="Difficulty" value={scenario.difficulty} />
        <DetailItem label="Nodes" value={scenario.nodes.length} />
        <DetailItem label="Latency Budget" value={`${scenario.workload.latency_budget} ms`} />
        <DetailItem label="CU Requirements" value={`CPU ${scenario.workload.cu.cpu_req}, Mem ${scenario.workload.cu.mem_req}`} />
        <DetailItem label="DU Requirements" value={`CPU ${scenario.workload.du.cpu_req}, Mem ${scenario.workload.du.mem_req}`} />
      </div>
    </div>
  );
}

function DetailItem({ label, value, mono }) {
  return (
    <div className="p-3 rounded-lg bg-surface-800/50 border border-surface-600/20">
      <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
      <p className={`text-slate-200 mt-0.5 ${mono ? "font-mono text-xs break-all" : ""}`}>{value}</p>
    </div>
  );
}

function PlacementCard({ label, nodeName, node, accent }) {
  const colors = accent === "violet"
    ? "border-violet-500/30 bg-violet-500/5"
    : "border-emerald-500/30 bg-emerald-500/5";

  return (
    <div className={`p-4 rounded-xl border ${colors}`}>
      <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">{label}</p>
      <p className="font-display text-lg font-semibold text-white">{nodeName}</p>
      {node && (
        <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-400">
          <span className="px-2 py-0.5 rounded bg-surface-600">{node.zone}</span>
          <span>CPU: {node.cpu_used}/{node.cpu_capacity}</span>
          <span>Mem: {node.mem_used}/{node.mem_capacity}</span>
          <span>Load: {node.load}</span>
        </div>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

function BaselineIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function MLIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
    </svg>
  );
}

function DatasetIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375" />
    </svg>
  );
}
