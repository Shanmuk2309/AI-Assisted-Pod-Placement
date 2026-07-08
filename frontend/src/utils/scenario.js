const ZONES = ["zone-a", "zone-b", "zone-c"];

export function createDefaultNode(index) {
  return {
    name: `node${index}`,
    zone: ZONES[index % ZONES.length],
    load: 0.3,
    cpu_capacity: 12,
    cpu_used: 3,
    mem_capacity: 32,
    mem_used: 8,
  };
}

export function createDefaultScenario() {
  const nodes = [createDefaultNode(0), createDefaultNode(1), createDefaultNode(2)];
  return {
    scenario_id: crypto.randomUUID(),
    difficulty: "medium",
    nodes,
    latency_matrix: buildLatencyMatrix(nodes),
    workload: {
      cu: { cpu_req: 2, mem_req: 3 },
      du: { cpu_req: 6, mem_req: 4 },
      latency_budget: 10,
    },
  };
}

export function buildLatencyMatrix(nodes) {
  const matrix = {};
  for (const n1 of nodes) {
    matrix[n1.name] = {};
    for (const n2 of nodes) {
      if (n1.name === n2.name) {
        matrix[n1.name][n2.name] = 1;
      } else if (n1.zone === n2.zone) {
        matrix[n1.name][n2.name] = 3;
      } else {
        matrix[n1.name][n2.name] = 8;
      }
    }
  }
  return matrix;
}

export function buildRandomLatencyMatrix(nodes) {
  const matrix = {};

  const randomInt = (min, max) =>
    Math.floor(Math.random() * (max - min + 1)) + min;

  // Initialize matrix
  nodes.forEach((node) => {
    matrix[node.name] = {};
  });

  // Fill only upper triangle and mirror values
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i; j < nodes.length; j++) {

      let latency;

      if (i === j) {
        latency = 1;
      } else if (nodes[i].zone === nodes[j].zone) {
        latency = randomInt(2, 4);
      } else {
        latency = randomInt(6, 10);
      }

      matrix[nodes[i].name][nodes[j].name] = latency;
      matrix[nodes[j].name][nodes[i].name] = latency;
    }
  }

  return matrix;
}

export function buildScenarioPayload(form) {
  return {
    scenario_id: form.scenario_id || crypto.randomUUID(),
    difficulty: form.difficulty,
    nodes: form.nodes.map((n) => ({
      name: n.name,
      zone: n.zone,
      load: Number(n.load),
      cpu_capacity: Number(n.cpu_capacity),
      cpu_used: Number(n.cpu_used),
      mem_capacity: Number(n.mem_capacity),
      mem_used: Number(n.mem_used),
    })),
    latency_matrix: form.latency_matrix,
    workload: {
      cu: {
        cpu_req: Number(form.workload.cu.cpu_req),
        mem_req: Number(form.workload.cu.mem_req),
      },
      du: {
        cpu_req: Number(form.workload.du.cpu_req),
        mem_req: Number(form.workload.du.mem_req),
      },
      latency_budget: Number(form.workload.latency_budget),
    },
  };
}

export { ZONES };
