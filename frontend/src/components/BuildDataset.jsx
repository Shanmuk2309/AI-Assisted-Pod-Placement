import { useState, useEffect, useRef } from "react";
import { generateDataset, getDatasetStatus } from "../api";

const POLL_INTERVAL_MS = 2000;

export default function BuildDataset() {
  const [starting, setStarting] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");
  const pollRef = useRef(null);

  const isRunning = status?.status === "running";

  function stopPolling() {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  async function refreshStatus() {
    try {
      const data = await getDatasetStatus();
      setStatus(data);

      if (data.status !== "running") {
        stopPolling();
      }
    } catch (err) {
      setError(err.message);
      stopPolling();
    }
  }

  function startPolling() {
    stopPolling();
    pollRef.current = setInterval(refreshStatus, POLL_INTERVAL_MS);
  }

  useEffect(() => {
    async function init() {
      try {
        const data = await getDatasetStatus();
        setStatus(data);
        if (data.status === "running") {
          startPolling();
        }
      } catch (err) {
        setError(err.message);
      }
    }
    init();
    return () => stopPolling();
  }, []);

  async function handleBuild() {
    setStarting(true);
    setError("");
    try {
      await generateDataset();
      await refreshStatus();
      startPolling();
    } catch (err) {
      setError(err.message);
    } finally {
      setStarting(false);
    }
  }

  return (
    <div className="card">
      <div className="mb-5">
        <h2 className="section-title">Build Training Dataset</h2>
        <p className="text-sm text-slate-400 mt-1">
          Evaluate all unprocessed scenarios using the scoring function and export to CSV
        </p>
      </div>

      <div className="p-4 rounded-xl bg-surface-700/50 border border-surface-600/30 mb-5">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-warning/10 text-warning">
            <DatabaseIcon />
          </div>
          <div className="text-sm text-slate-400 leading-relaxed">
            <p>
              This runs <span className="text-slate-300 font-medium">Ray parallel evaluation</span> in
              the background. Every node-pair placement is scored and saved to{" "}
              <code className="text-accent-light bg-surface-600 px-1.5 py-0.5 rounded text-xs">
                data/dataset.csv
              </code>
            </p>
            <p className="mt-2 text-xs text-slate-500">
              Requires scenarios to be generated first. Processing may take several minutes for large batches.
            </p>
          </div>
        </div>
      </div>

      <button
        onClick={handleBuild}
        disabled={starting || isRunning}
        className="btn-primary"
      >
        {starting || isRunning ? (
          <>
            <Spinner />
            {isRunning ? "Generating dataset…" : "Starting…"}
          </>
        ) : (
          <>
            <DatabaseIcon />
            Build Dataset
          </>
        )}
      </button>

      {status && <StatusBanner status={status} />}

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}

function StatusBanner({ status }) {
  if (status.status === "idle") return null;

  const styles = {
    running: "bg-accent/10 border-accent/20 text-accent-light",
    completed: "bg-success/10 border-success/20 text-success",
    failed: "bg-red-500/10 border-red-500/20 text-red-400",
  };

  return (
    <div className={`mt-4 p-4 rounded-lg border text-sm ${styles[status.status] || styles.running}`}>
      <div className="flex items-center gap-2 font-medium">
        {status.status === "running" && <Spinner />}
        {status.status === "completed" && <CheckIcon />}
        {status.status === "failed" && <ErrorIcon />}
        <span>
          {status.status === "running" && "Generation in progress"}
          {status.status === "completed" && "Generation completed"}
          {status.status === "failed" && "Generation failed"}
        </span>
      </div>

      <p className="mt-2 opacity-90">{status.message}</p>

      {status.status === "completed" && status.rows_generated != null && (
        <div className="mt-3 grid sm:grid-cols-2 gap-2 text-xs opacity-80">
          <span>Rows generated: <strong>{status.rows_generated}</strong></span>
          <span>Scenarios used: <strong>{status.scenarios_used}</strong></span>
          {status.csv_file && <span>CSV: <strong>{status.csv_file}</strong></span>}
          {status.jsonl_file && <span>JSONL: <strong>{status.jsonl_file}</strong></span>}
        </div>
      )}

      {status.status === "failed" && status.error && (
        <p className="mt-2 text-xs opacity-80">{status.error}</p>
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

function CheckIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function DatabaseIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375" />
    </svg>
  );
}
