import GenerateScenarios from "./components/GenerateScenarios";
import BuildDataset from "./components/BuildDataset";
import ScenarioForm from "./components/ScenarioForm";
import UserGuide from "./components/UserGuide";

export default function App() {
  return (
    <div className="min-h-screen">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-accent/8 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-violet-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-72 h-72 bg-emerald-600/5 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative border-b border-surface-600/30 bg-surface-900/80 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-3">
          <div className="p-2 rounded-xl bg-accent/10 border border-accent/20">
            <svg className="w-6 h-6 text-accent-light" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a3 3 0 013-3h13.5a3 3 0 013 3" />
            </svg>
          </div>
          <div>
            <h1 className="font-display text-lg font-bold text-white tracking-tight">
              AI Pod Placement Advisor
            </h1>
            <p className="text-xs text-slate-500">
              CU/DU workload placement optimization
            </p>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        <div className="grid lg:grid-cols-2 gap-6">
          <GenerateScenarios />
          <BuildDataset />
        </div>
        <UserGuide />
        <ScenarioForm />
      </main>

      <footer className="relative text-center py-6 text-xs text-slate-600">
        Scenario Service :8000 · Advisor API :8001 · Frontend :5173
      </footer>
    </div>
  );
}
