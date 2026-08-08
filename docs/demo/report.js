window.GRAPHMEDIC_STATIC_REPORT = {
  summary: {assets_scanned: 6, findings: 6, downstream_edges: 5, severity: {critical: 1, high: 2, medium: 1, low: 2}},
  findings: [
    {
      id: 'orders-critical', score: 115, severity: 'critical',
      title: 'Owner Gap + Documentation Gap + Deprecated Dependency',
      asset: {name: 'Orders', urn: 'urn:li:dataset:(urn:li:dataPlatform:graphmedic_demo,demo_ops.orders_clean,PROD)'},
      evidence: ['No owner is recorded in DataHub', 'No human-readable description is recorded', '1 downstream asset is in the blast radius', 'A deprecated upstream asset still feeds this dataset'],
      actions: [{kind: 'add_tag', value: 'GraphMedicReviewed'}, {kind: 'append_description', value: 'GraphMedic review: metadata stewardship is required. Current synthetic lineage shows 1 downstream asset.'}]
    },
    {
      id: 'revenue-high', score: 55, severity: 'high', title: 'Owner Gap + Documentation Gap',
      asset: {name: 'Revenue', urn: 'urn:li:dataset:(urn:li:dataPlatform:graphmedic_demo,demo_analytics.daily_revenue,PROD)'},
      evidence: ['No owner is recorded in DataHub', 'No human-readable description is recorded', '1 downstream asset is in the blast radius'],
      actions: [{kind: 'add_tag', value: 'GraphMedicReviewed'}, {kind: 'append_description', value: 'GraphMedic review: metadata stewardship is required. Current synthetic lineage shows 1 downstream asset.'}]
    },
    {
      id: 'dashboard-high', score: 50, severity: 'high', title: 'Owner Gap + Documentation Gap',
      asset: {name: 'Dashboard', urn: 'urn:li:dataset:(urn:li:dataPlatform:graphmedic_demo,demo_analytics.executive_snapshot,PROD)'},
      evidence: ['No owner is recorded in DataHub', 'No human-readable description is recorded'],
      actions: [{kind: 'add_tag', value: 'GraphMedicReviewed'}]
    }
  ],
  tool_evidence: [
    {tool: 'search', argument_keys: ['num_results', 'query'], duration_ms: 678, status: 'verified'},
    {tool: 'get_entities', argument_keys: ['urns'], duration_ms: 1967, status: 'verified'},
    {tool: 'get_lineage', argument_keys: ['max_hops', 'max_results', 'upstream', 'urn'], duration_ms: 441, status: 'verified'},
    {tool: 'get_lineage', argument_keys: ['max_hops', 'max_results', 'upstream', 'urn'], duration_ms: 487, status: 'verified'}
  ]
};
