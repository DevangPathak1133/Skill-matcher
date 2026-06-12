document.getElementById('upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const jds = document.getElementById('jds').files;
  const resumes = document.getElementById('resumes').files;
  if (jds.length === 0 || resumes.length === 0) {
    alert('Please select at least one JD and one resume.');
    return;
  }
  const fd = new FormData();
  for (let f of jds) fd.append('jds', f);
  for (let f of resumes) fd.append('resumes', f);

  const resDiv = document.getElementById('results');
  resDiv.innerHTML = '<p style="color: #666;">Analyzing skills...</p>';

  const resp = await fetch('/match', { method: 'POST', body: fd });
  if (!resp.ok) {
    const err = await resp.json();
    resDiv.innerHTML = '<pre style="color: red;">' + (err.error || 'Server error') + '</pre>';
    return;
  }
  const data = await resp.json();
  resDiv.innerHTML = '';
  
  for (let r of data.results) {
    const section = document.createElement('div');
    section.className = 'job-section';
    
    // Job title and required skills
    const h2 = document.createElement('h2');
    h2.textContent = 'Job: ' + r.jd;
    section.appendChild(h2);
    
    const skillsDiv = document.createElement('div');
    skillsDiv.className = 'required-skills';
    skillsDiv.innerHTML = '<strong>Required Skills:</strong> ' + r.required_skills.join(', ');
    section.appendChild(skillsDiv);
    
    // Results table
    const table = document.createElement('table');
    table.innerHTML = `
      <tr>
        <th>Resume</th>
        <th>Match %</th>
        <th>Matched Skills</th>
        <th>Missing Skills</th>
        <th>Extra Skills</th>
      </tr>
    `;
    
    for (let m of r.matches) {
      const tr = document.createElement('tr');
      const matchedBg = m.match_percentage >= 80 ? '#d4edda' : m.match_percentage >= 50 ? '#fff3cd' : '#f8d7da';
      tr.style.backgroundColor = matchedBg;
      
      const matchColor = m.match_percentage >= 80 ? '#28a745' : m.match_percentage >= 50 ? '#ffc107' : '#dc3545';
      
      tr.innerHTML = `
        <td>${m.resume}</td>
        <td><strong style="color: ${matchColor}; font-size: 1.1em;">${m.match_percentage}%</strong></td>
        <td><span class="skill-badge success">${m.matched_skills.join(', ') || 'None'}</span></td>
        <td><span class="skill-badge warning">${m.missing_skills.join(', ') || 'None'}</span></td>
        <td><span class="skill-badge info">${m.extra_skills.join(', ') || 'None'}</span></td>
      `;
      table.appendChild(tr);
    }
    section.appendChild(table);
    resDiv.appendChild(section);
  }
});

