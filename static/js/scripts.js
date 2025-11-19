// Note: Password validation is performed on the server.
// Do not hardcode or fetch admin passwords client-side.

// Fetch apps data from the backend and render tiles
fetch('/get_apps')
  .then(response => response.json())
  .then(apps => {
    const tilesContainer = document.getElementById('tiles-container');

    apps.forEach(app => {
      const tile = document.createElement('div');
      tile.classList.add('tile');
      tile.setAttribute('data-name', app.name);
      tile.innerHTML = `
        <button class="delete-btn" title="Remove" aria-label="Remove"
                style="float:right; border:none; background:transparent; color:#a00; font-weight:bold; font-size:18px; cursor:pointer;">−</button>
        <a href="${app.url}" class="tile-link">
            <div class="tile-content">
                <img src="${app.icon}" alt="App Icon" class="tile-icon">
                <h2 class="tile-title">${app.name}</h2>
                <p class="tile-description">${app.description}</p>
            </div>
        </a>
      `;
      tilesContainer.appendChild(tile);

      // Attach delete handler for this tile
      const delBtn = tile.querySelector('.delete-btn');
      attachDeleteHandler(delBtn, app.name, tile);
    });

    // Ensure the "Add New Application" button is always at the end
    const addTileButton = document.getElementById('addTileButton');
    tilesContainer.appendChild(addTileButton);

    // Add event listener to the "Add New Application" button
    addTileButton.addEventListener('click', showForm);
  })
  .catch(error => console.error('Error fetching apps:', error));

// Show form to add new tile
function showForm() {
  document.getElementById('formModal').style.display = 'block';
}

// Close form modal (used by inline onClick in HTML)
function closeForm() {
  document.getElementById('formModal').style.display = 'none';
}

// Handle form submission
document.getElementById('newTileForm').onsubmit = function (event) {
  event.preventDefault();

  // Gather form data
  const name = document.getElementById('name').value;
  const url = document.getElementById('url').value;
  const icon = document.getElementById('icon').value;
  const description = document.getElementById('description').value;
  const password = document.getElementById('password').value;

  // Send data to backend to save in MongoDB
  fetch('/add_new_app', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, url, icon, description, admin_password: password }),
  })
    .then(r => r.json().then(data => ({ ok: r.ok, status: r.status, data })))
    .then(({ ok, status, data }) => {
      if (ok && data.success) {
        // Add the new tile to the page dynamically
        addNewTile(name, url, icon, description);
        closeForm();
        alert('Tile added successfully!');
      } else {
        const msg = (data && data.error) ? data.error : 'Failed to add tile';
        if (status === 401) {
          alert('Unauthorized: ' + msg);
        } else {
          alert(msg);
        }
      }
    });
};

// Dynamically add new tile to the tiles container
function addNewTile(name, url, icon, description) {
  const tilesContainer = document.getElementById('tiles-container');
  const tile = document.createElement('div');
  tile.classList.add('tile');
  tile.setAttribute('data-name', name);
  tile.innerHTML = `
    <button class="delete-btn" title="Remove" aria-label="Remove"
            style="float:right; border:none; background:transparent; color:#a00; font-weight:bold; font-size:18px; cursor:pointer;">−</button>
    <a href="${url}" class="tile-link">
        <div class="tile-content">
            <img src="${icon}" alt="App Icon" class="tile-icon">
            <h2 class="tile-title">${name}</h2>
            <p class="tile-description">${description}</p>
        </div>
    </a>
  `;
  tilesContainer.appendChild(tile);

  // Attach delete handler for this new tile
  const delBtn = tile.querySelector('.delete-btn');
  attachDeleteHandler(delBtn, name, tile);

  // Move the "Add New Application" button to the last position
  const addTileButton = document.getElementById('addTileButton');
  tilesContainer.appendChild(addTileButton);
}

// Attach delete functionality to a button for a specific tile
function attachDeleteHandler(buttonEl, appName, tileEl) {
  if (!buttonEl) return;
  buttonEl.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const entered = window.prompt('Enter admin password to remove this app:');
    if (entered === null) return; // user cancelled

    fetch('/delete_app', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: appName, admin_password: entered })
    })
      .then(r => r.json().then(data => ({ ok: r.ok, status: r.status, data })))
      .then(({ ok, status, data }) => {
        if (ok && data.success) {
          // remove tile from DOM
          if (tileEl && tileEl.parentNode) {
            tileEl.parentNode.removeChild(tileEl);
          }
          alert('App removed.');
        } else {
          const msg = data && data.error ? data.error : 'Failed to remove app';
          if (status === 401) {
            alert('Unauthorized: ' + msg);
          } else {
            alert('Failed to remove app' + (msg ? `: ${msg}` : ''));
          }
        }
      })
      .catch(() => alert('Network error while removing app'));
  });
}
