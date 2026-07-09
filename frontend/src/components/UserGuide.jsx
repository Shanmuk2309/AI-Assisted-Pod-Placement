import { useState } from "react";

export default function UserGuide() {
  const [expandedSection, setExpandedSection] = useState(null);
  const [showGuide, setShowGuide] = useState(true);

  const sections = [
    {
      id: "nodes",
      title: "📍 Cluster Nodes",
      description: "Define the compute nodes in your Kubernetes cluster",
      content: [
        {
          label: "Node Name",
          example: "node0, node1, worker-1",
          explanation: "Unique identifier for each node in the cluster",
        },
        {
          label: "Zone",
          example: "zone-a, zone-b, zone-c",
          explanation:
            "Availability zone for the node. Nodes in the same zone have lower latency.",
        },
        {
          label: "CPU Capacity",
          example: "8, 16, 32 cores",
          explanation: "Total CPU cores available on this node.",
        },
        {
          label: "Memory Capacity",
          example: "32, 64, 128 GB",
          explanation: "Total memory available on this node.",
        },
        {
          label: "Current CPU Used",
          example: "4, 8 cores",
          explanation: "CPU already occupied by existing workloads.",
        },
        {
          label: "Current Memory Used",
          example: "16, 32 GB",
          explanation: "Memory already occupied by existing workloads.",
        },
        {
          label: "Load Factor",
          example: "0.3, 0.5, 0.8 (0-1)",
          explanation:
            "Current utilization level of the node. 0 = idle, 1 = fully loaded.",
        },
      ],
    },
    {
      id: "latency",
      title: "🔗 Latency Matrix",
      description: "Network latency between nodes",
      content: [
        {
          label: "Same Zone Latency",
          example: "2 - 4 ms",
          explanation:
            "Communication latency between nodes in the same availability zone.",
        },
        {
          label: "Different Zone Latency",
          example: "6 - 10 ms",
          explanation:
            "Communication latency between nodes in different zones.",
        },
        {
          label: "Same Node Latency",
          example: "1 ms",
          explanation: "Latency when CU and DU are placed on the same node.",
        },
      ],
    },
    {
      id: "workload",
      title: "⚙️ Workload Configuration",
      description: "Define the CU and DU workload requirements",
      content: [
        {
          label: "Compute Unit (CU)",
          example: "CPU: 2 cores | Memory: 4 GB",
          explanation:
            "Resources required for the Compute Unit workload.",
        },
        {
          label: "Data Unit (DU)",
          example: "CPU: 6 cores | Memory: 8 GB",
          explanation:
            "Resources required for the Data Unit workload.",
        },
        {
          label: "Latency Budget",
          example: "10 - 20 ms",
          explanation:
            "Maximum acceptable latency between CU and DU.",
        },
      ],
    },
    {
      id: "difficulty",
      title: "📊 Scenario Difficulty",
      description: "Controls how constrained the generated scenario is",
      content: [
        {
          label: "Easy",
          example: "4-6 nodes | ~30% load",
          explanation:
            "Plenty of free resources with minimal placement constraints.",
        },
        {
          label: "Medium",
          example: "6-8 nodes | ~60% load",
          explanation:
            "Balanced resource availability with moderate constraints.",
        },
        {
          label: "Hard",
          example: "8-10 nodes | ~80% load",
          explanation:
            "Highly constrained environment requiring optimized placement.",
        },
      ],
    },
  ];

  return (
    <div className="card overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between pb-5 border-b border-surface-600/40">

        <div>
          <h2 className="font-display text-2xl font-bold text-white">
            📚 User Guide
          </h2>

          <p className="text-slate-400 mt-1">
            Understand every metric before creating a custom scenario.
          </p>
        </div>

        <button
          onClick={() => setShowGuide(!showGuide)}
          className="btn-primary px-4 py-2"
        >
          {showGuide ? "Hide Guide" : "Show Guide"}
        </button>

      </div>

      {showGuide && (
        <div className="mt-6 space-y-4">

          {sections.map((section) => (
            <div
              key={section.id}
              className="rounded-xl border border-surface-600 bg-surface-700/60 overflow-hidden transition-all"
            >

              <button
                onClick={() =>
                  setExpandedSection(
                    expandedSection === section.id ? null : section.id
                  )
                }
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-surface-600/50 transition"
              >

                <div className="text-left">
                  <h3 className="font-semibold text-white text-lg">
                    {section.title}
                  </h3>

                  <p className="text-sm text-slate-400 mt-1">
                    {section.description}
                  </p>
                </div>

                <svg
                  className={`w-5 h-5 text-accent-light transition-transform duration-300 ${
                    expandedSection === section.id ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>

              </button>

              {expandedSection === section.id && (

                <div className="px-6 py-5 bg-surface-800 border-t border-surface-600">

                  <div className="space-y-5">

                    {section.content.map((item, idx) => (

                      <div
                        key={idx}
                        className="pb-4 border-b border-surface-600 last:border-b-0"
                      >

                        <div className="flex flex-wrap justify-between items-start gap-2 mb-2">

                          <h4 className="font-semibold text-white">
                            {item.label}
                          </h4>

                          <span className="px-3 py-1 rounded-full bg-accent/20 border border-accent/30 text-accent-light text-xs font-mono">
                            {item.example}
                          </span>

                        </div>

                        <p className="text-slate-300 leading-relaxed">
                          {item.explanation}
                        </p>

                      </div>

                    ))}

                  </div>

                </div>

              )}

            </div>
          ))}

          <div className="mt-6 rounded-xl border border-accent/30 bg-accent/10 p-5">

            <p className="text-slate-300 leading-relaxed">
              <span className="font-semibold text-accent-light">
                💡 Pro Tip:
              </span>{" "}
              The recommendation engine performs best when the scenario closely
              reflects your actual Kubernetes cluster. Accurate node capacities,
              workload requirements, and latency values produce more meaningful
              placement recommendations.
            </p>

          </div>

        </div>
      )}

    </div>
  );
}