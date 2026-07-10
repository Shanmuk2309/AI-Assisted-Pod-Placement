import { useState, useEffect } from "react";
import { clearScenarios, generateScenarios, listScenarios } from "../api";

export default function GenerateScenarios() {
  const [count, setCount] = useState(10);
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [totalScenarios, setTotalScenarios] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function refreshCount() {
    try {
      const data = await listScenarios();
      setTotalScenarios(Array.isArray(data) ? data.length : 0);
    } catch {
      setTotalScenarios(0);
    }
  }

  async function handleGenerate() {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const data = await generateScenarios(count);
      setMessage(data.message);
      await refreshCount();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleClear() {
    setClearing(true);
    setError("");
    setMessage("");
    try {
      const data = await clearScenarios();
      setMessage(data.message);
      await refreshCount();
    } catch (err) {
      setError(err.message);
    } finally {
      setClearing(false);
    }
  }

  useEffect(() => {
    refreshCount();
  }, []);

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-5">
        <div>
          <h2 className="section-title">Generate Scenarios</h2>
          <p className="text-sm text-slate-400 mt-1">
            Create synthetic cluster scenarios with varying difficulty levels
          </p>
        </div>
        {totalScenarios !== null && (
          <span className="status-badge bg-accent/10 text-accent-light border border-accent/20">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-light animate-pulse" />
            {totalScenarios} in DB
          </span>
        )}
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-end">
        <div className="flex-1 w-full">
          <label className="field-label">Number of Scenarios</label>
          <input
            type="number"
            min={1}
            max={10000}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="w-full"
          />
          <p className="text-xs text-slate-500 mt-1.5">
            Rotates through easy, medium, and hard difficulties
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <button
            onClick={() => {
              if (window.confirm("Delete all scenarios from the database?")) {
                handleClear();
              }
            }}
            disabled={loading || clearing}
            className="btn-secondary w-full sm:w-auto"
          >
            {clearing ? (
              <>
                <Spinner />
                Clearing…
              </>
            ) : (
              <>
                <TrashIcon />
                Clear
              </>
            )}
          </button>
          <button
            onClick={handleGenerate}
            disabled={loading || clearing || count < 1}
            className="btn-primary w-full sm:w-auto"
          >
            {loading ? (
              <>
                <Spinner />
                Generating…
              </>
            ) : (
              <>
                <PlusIcon />
                Generate
              </>
            )}
          </button>
        </div>
      </div>

      {message && (
        <div className="mt-4 p-3 rounded-lg bg-success/10 border border-success/20 text-success text-sm">
          {message}
        </div>
      )}
      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
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

function PlusIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.164h-5.16c-1.18 0-2.09.984-2.09 2.164v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
    </svg>
  );
}
