const form = document.querySelector('#lookup-form');
const status = document.querySelector('#status');
const results = document.querySelector('#results');
const button = form.querySelector('button');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  results.replaceChildren();
  status.textContent = 'Checking selected services…';
  button.disabled = true;
  try {
    const response = await fetch('/api/lookup', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email: form.elements.email.value.trim()})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Lookup unavailable');
    const heading = document.createElement('h2');
    heading.textContent = 'Results';
    const list = document.createElement('ul');
    for (const item of data.results) {
      const row = document.createElement('li');
      row.textContent = `${item.service}: ${item.status.replaceAll('_', ' ')}`;
      list.append(row);
    }
    results.append(heading, list);
    status.textContent = 'Check finished. Treat signals as uncertain.';
  } catch (error) {
    status.textContent = error instanceof TypeError ? 'Local backend unavailable. Start it using the README instructions.' : error.message;
  } finally {
    button.disabled = false;
  }
});
