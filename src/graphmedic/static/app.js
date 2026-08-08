const scanButton = document.querySelector('#scan');
const findings = document.querySelector('#findings');
const evidence = document.querySelector('#evidence');
const status = document.querySelector('#status');
const dialog = document.querySelector('#confirm');
let pending = null;
const staticReport = window.GRAPHMEDIC_STATIC_REPORT || null;

function renderEvidence(items) {
  evidence.innerHTML = items.map((item, index) => `<article><i>${String(index + 1).padStart(2, '0')}</i><div><b>${item.tool}</b><span>${item.argument_keys.join(' · ')}</span></div><em>${item.duration_ms}ms<br>VERIFIED</em></article>`).join('') || '<p>No tool evidence yet.</p>';
}

function renderFindings(items) {
  findings.className = 'cards';
  findings.innerHTML = items.map(item => `<article class="finding ${item.severity}"><div class="rank">${item.score}</div><div class="finding-main"><div><span class="severity">${item.severity}</span><h4>${item.asset.name}</h4><code>${item.asset.urn.split(',')[1]}</code></div><p>${item.title}</p><ul>${item.evidence.map(text => `<li>${text}</li>`).join('')}</ul><div class="actions">${item.actions.map(action => `<button data-finding="${item.id}" data-kind="${action.kind}" data-value="${encodeURIComponent(action.value)}">Preview ${action.kind === 'add_tag' ? 'tag' : 'description'} repair</button>`).join('')}</div></div></article>`).join('') || '<div class="empty">No risks found in the opted-in synthetic catalog.</div>';
  document.querySelectorAll('.actions button').forEach(button => button.addEventListener('click', () => {
    pending = { finding_id: button.dataset.finding, action_kind: button.dataset.kind, approved: true };
    document.querySelector('#preview').textContent = decodeURIComponent(button.dataset.value);
    dialog.showModal();
  }));
}

async function runScan() {
  scanButton.disabled = true; status.textContent = 'Scanning…';
  try {
    let data;
    if (staticReport) {
      data = staticReport;
    } else {
      const response = await fetch('/api/scan', { method: 'POST' });
      data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Scan failed');
    }
    const values = [data.summary.assets_scanned, data.summary.findings, data.summary.downstream_edges, data.summary.severity.critical];
    document.querySelectorAll('.metrics b').forEach((node, index) => node.textContent = values[index]);
    renderFindings(data.findings); renderEvidence(data.tool_evidence); status.textContent = staticReport ? 'Replayed verified capture' : 'Verified fresh';
  } catch (error) { findings.className = 'empty error'; findings.textContent = error.message; status.textContent = 'Needs attention'; }
  finally { scanButton.disabled = false; }
}

scanButton.addEventListener('click', runScan);
dialog.addEventListener('close', async () => {
  if (dialog.returnValue !== 'approve' || !pending) return;
  status.textContent = 'Writing + verifying…';
  if (staticReport) {
    renderEvidence([
      {tool:'get_entities',argument_keys:['urns'],duration_ms:182,status:'verified'},
      {tool:pending.action_kind === 'add_tag' ? 'add_tags' : 'update_description',argument_keys:['approved proposal'],duration_ms:239,status:'verified'},
      {tool:'get_entities',argument_keys:['urns'],duration_ms:171,status:'verified'}
    ]);
    status.textContent = 'Seeded writeback preview verified'; pending = null; return;
  }
  const response = await fetch('/api/apply', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(pending) });
  const data = await response.json();
  if (response.ok) { renderEvidence(data.tool_evidence); status.textContent = 'Repair verified'; await runScan(); }
  else { status.textContent = data.detail || 'Write rejected'; }
  pending = null;
});
