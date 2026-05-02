/** Same origin as this page when served from Flask; fallback for file:// dev. */
const API_BASE =
  window.location.protocol === "file:" || !window.location.origin
    ? "http://127.0.0.1:5000"
    : window.location.origin;

const startPage = document.getElementById("startPage");
const canvasPage = document.getElementById("canvasPage");

const createCanvasBtn = document.getElementById("createCanvasBtn");
const openCanvasBtn = document.getElementById("openCanvasBtn");
const backBtn = document.getElementById("backBtn");
const addStickyBtn = document.getElementById("addStickyBtn");
const canvasArea = document.getElementById("canvasArea");
const canvasNameInput = document.getElementById("canvasNameInput");
const canvasList = document.getElementById("canvasList");
const uiStatus = document.getElementById("uiStatus");
const groupSelect = document.getElementById("groupSelect");
const applyGroupBtn = document.getElementById("applyGroupBtn");
const newGroupInput = document.getElementById("newGroupInput");
const newGroupBtn = document.getElementById("newGroupBtn");
const groupHelp = document.getElementById("groupHelp");

const backgroundColorInput = document.getElementById("backgroundColorInput");
const borderColorInput = document.getElementById("borderColorInput");

let currentCanvasId = null;
let currentCanvasName = null;
let selectedStickyNote = null;

const GROUP_BG_PALETTE = [
  "#ffef88",
  "#c8e6c9",
  "#bbdefb",
  "#e1bee7",
  "#ffe0b2",
  "#b2dfdb",
  "#f8bbd0",
  "#d7ccc8",
  "#b2ebf2",
  "#fff9c4"
];

function colorForGroup(groupName) {
  const key = String(groupName || "default");
  let h = 0;
  for (let i = 0; i < key.length; i++) {
    h = ((h << 5) - h) + key.charCodeAt(i);
    h |= 0;
  }
  const idx = Math.abs(h) % GROUP_BG_PALETTE.length;
  return GROUP_BG_PALETTE[idx];
}

function applyGroupStyleToSticky(stickyEl) {
  const g = stickyEl.dataset.collection || "default";
  stickyEl.style.backgroundColor = colorForGroup(g);
  stickyEl.style.borderColor = "rgba(0,0,0,0.35)";
  const badge = stickyEl.querySelector(".note-group-badge");
  if (badge) {
    badge.textContent = g === "default" ? "Ungrouped" : g;
    badge.title = g;
  }
}

function selectStickyNote(stickyEl) {
  document.querySelectorAll(".sticky-note.selected").forEach((n) => {
    n.classList.remove("selected");
  });
  selectedStickyNote = stickyEl || null;
  if (selectedStickyNote) {
    selectedStickyNote.classList.add("selected");
    if (groupSelect) {
      groupSelect.value = selectedStickyNote.dataset.collection || "";
    }
    setUiStatus(`Selected note ${selectedStickyNote.dataset.noteId}.`);
  }
}

async function refreshGroupSelectDropdown() {
  if (!currentCanvasId || !groupSelect) {
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/api/canvases/${currentCanvasId}/groups`);
    const groups = await response.json();
    if (!response.ok) {
      console.error("Could not load groups:", groups);
      return;
    }
    groupSelect.innerHTML = "";

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "(Assign selected to group...)";
    groupSelect.appendChild(placeholder);

    groups.forEach((g) => {
      const opt = document.createElement("option");
      opt.value = g.name;
      opt.textContent = g.name === "default"
        ? `Ungrouped (${g.count})`
        : `${g.name} (${g.count})`;
      groupSelect.appendChild(opt);
    });

    const newOpt = document.createElement("option");
    newOpt.value = "__new__";
    newOpt.textContent = "(New group...)";
    groupSelect.appendChild(newOpt);
  } catch (e) {
    console.error("Error loading groups:", e);
  }
}

async function assignSelectedToGroup(collectionName) {
  const trimmed = String(collectionName || "").trim();
  if (!trimmed) {
    setUiStatus("Group name cannot be empty.");
    alert("Group name cannot be empty.");
    return;
  }
  if (!selectedStickyNote) {
    setUiStatus("Select a sticky note first, then choose a group.");
    alert("Select a sticky note first.");
    return;
  }
  const noteId = selectedStickyNote.dataset.noteId;

  try {
    const response = await fetch(`${API_BASE}/api/canvases/${currentCanvasId}/notes/${noteId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ collection: trimmed })
    });
    const data = await response.json();
    if (!response.ok) {
      setUiStatus(data.error || "Could not update group.");
      alert(data.error || "Could not update group.");
      return;
    }
    selectedStickyNote.dataset.collection = trimmed;
    applyGroupStyleToSticky(selectedStickyNote);
    setUiStatus(`Assigned note ${noteId} to group "${trimmed}".`);
    await refreshGroupSelectDropdown();
    if (groupSelect) {
      groupSelect.value = "";
    }
  } catch (error) {
    setUiStatus("Could not connect to backend while assigning group.");
    alert("Could not connect to backend.");
    console.error("Connection error:", error);
  }
}

function setUiStatus(message) {
  if (uiStatus) {
    uiStatus.textContent = message || "";
  }
  if (groupHelp) {
    groupHelp.textContent = message || "Click a sticky, then choose a group.";
  }
  if (message) {
    console.warn("[TEMA]", message);
  }
}

function showUserMessage(message) {
  setUiStatus(message);
  try {
    window.alert(message);
  } catch (e) {
    /* ignore */
  }
}

if (!createCanvasBtn || !openCanvasBtn) {
  setUiStatus("UI error: buttons not found (check index.html).");
} else {
createCanvasBtn.addEventListener("click", async () => {
  console.log("Create New Canvas button clicked", "API_BASE=", API_BASE);

  const canvasName = (canvasNameInput && canvasNameInput.value
    ? canvasNameInput.value
    : ""
  ).trim();

  if (!canvasName) {
    showUserMessage("Enter a canvas name in the box above, then click Create again.");
    return;
  }

  setUiStatus("Creating canvas…");

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    const response = await fetch(`${API_BASE}/api/canvases`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name: canvasName }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    const raw = await response.text();
    let data;
    try {
      data = JSON.parse(raw);
    } catch (parseErr) {
      console.error("Create canvas: non-JSON body", response.status, raw.slice(0, 400));
      showUserMessage(
        "Server returned non-JSON (HTTP " +
          response.status +
          "). Open the Flask terminal — is Postgres running and is dev_db set up?"
      );
      return;
    }

    if (!response.ok) {
      showUserMessage("Could not create canvas: " + (data.error || raw));
      console.error("Backend error:", data);
      return;
    }

    console.log("Created canvas:", data);

    if (data.id == null || data.name == null) {
      showUserMessage("Unexpected response from server (missing id or name). Check Flask /api/canvases POST.");
      return;
    }

    currentCanvasId = data.id;
    currentCanvasName = data.name;

    const toolbarTitle = document.querySelector(".toolbar h2");
    if (toolbarTitle) {
      toolbarTitle.textContent = `Canvas: ${currentCanvasName}`;
    }

    canvasArea.innerHTML = "";

    startPage.classList.add("hidden");
    startPage.style.display = "none";
    canvasPage.classList.remove("hidden");
    canvasPage.style.display = "flex";
    setUiStatus("");
    await refreshGroupSelectDropdown();
  } catch (error) {
    const msg =
      error && error.name === "AbortError"
        ? "Request timed out. Is Flask running on the same port as this page (see API_BASE in console)?"
        : "Could not reach the server. Start Flask (python backend/app.py) then try again. Details: " +
          (error && error.message ? error.message : String(error));
    showUserMessage(msg);
    console.error("Connection error:", error);
  }
});





openCanvasBtn.addEventListener("click", async () => {
  console.log("Open Existing Canvas button clicked");

  try {
    const response = await fetch(`${API_BASE}/api/canvases`);
    const canvases = await response.json();

    if (!response.ok) {
      alert("Could not load canvases.");
      console.error("Backend error:", canvases);
      return;
    }

    console.log("Loaded canvases:", canvases);

    canvasList.innerHTML = "";

    if (canvases.length === 0) {
      canvasList.textContent = "No canvases found.";
      return;
    }

    canvases.forEach((canvas) => {
      const canvasButton = document.createElement("button");
      canvasButton.textContent = `${canvas.id}: ${canvas.name}`;
      canvasButton.style.backgroundColor = "#666";
      canvasButton.style.marginTop = "8px";

      canvasButton.addEventListener("click", () => {
        currentCanvasId = canvas.id;
        currentCanvasName = canvas.name;

        console.log("Opened canvas:", {
          id: currentCanvasId,
          name: currentCanvasName
        });

        document.querySelector(".toolbar h2").textContent =
          `Canvas: ${currentCanvasName}`;

        startPage.classList.add("hidden");
        startPage.style.display = "none";
        canvasPage.classList.remove("hidden");
        canvasPage.style.display = "flex";

        loadStickyNotesForCurrentCanvas();
        refreshGroupSelectDropdown();
      });

      canvasList.appendChild(canvasButton);
    });

  } catch (error) {
    alert("Could not connect to backend.");
    console.error("Connection error:", error);
  }
});

}

if (backBtn) {
  backBtn.addEventListener("click", () => {
    canvasPage.classList.add("hidden");
    canvasPage.style.display = "none";
    startPage.classList.remove("hidden");
    startPage.style.display = "";
  });
}

async function handleGroupSelection(selected) {
  if (!selected) {
    return;
  }
  if (selected === "__new__") {
    setUiStatus("Type a group name in 'New group name', then click Create/Assign.");
    return;
  }
  await assignSelectedToGroup(selected);
  groupSelect.value = "";
}

if (groupSelect) {
  groupSelect.addEventListener("change", async () => {
    setUiStatus(`Group picker selected "${groupSelect.value || "(none)"}".`);
    await handleGroupSelection(groupSelect.value);
  });
}

if (applyGroupBtn) {
  applyGroupBtn.addEventListener("click", async () => {
    if (!groupSelect || !groupSelect.value) {
      setUiStatus("Choose a group first, then click Apply.");
      return;
    }
    setUiStatus(`Applying group "${groupSelect.value}"...`);
    await handleGroupSelection(groupSelect.value);
  });
}

if (newGroupBtn) {
  newGroupBtn.addEventListener("click", async () => {
    const name = (newGroupInput && newGroupInput.value ? newGroupInput.value : "").trim();
    if (!name) {
      setUiStatus("Enter a new group name first.");
      return;
    }
    await assignSelectedToGroup(name);
    if (newGroupInput) {
      newGroupInput.value = "";
    }
  });
}

function makeStickyDraggable(stickyNote) {
  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  stickyNote.addEventListener("mousedown", (event) => {
      if (event.target.closest("button")) {
        return;
      }
      if (event.target.classList.contains("sticky-note-text")) {
      return;
      }

      selectStickyNote(stickyNote);
      isDragging = true;
      stickyNote.classList.add("dragging");

      offsetX = event.clientX - stickyNote.offsetLeft;
      offsetY = event.clientY - stickyNote.offsetTop;
  });


  document.addEventListener("mousemove", (event) => {
      if (!isDragging) return;

      stickyNote.style.left = `${event.clientX - offsetX}px`;
      stickyNote.style.top = `${event.clientY - offsetY}px`;
  });

  document.addEventListener("mouseup", () => {
      if (isDragging) {
        isDragging = false;
        stickyNote.classList.remove("dragging");
        saveStickyNote(stickyNote);
      }
  });
}

function createStickyNoteElement(noteData) {
  const stickyNote = document.createElement("div");
  stickyNote.classList.add("sticky-note");

  stickyNote.dataset.noteId = noteData.id;
  stickyNote.dataset.collection = (noteData.collection && String(noteData.collection).trim()) || "default";

  stickyNote.addEventListener("click", (event) => {
    event.stopPropagation();

    if (selectedNote) {
      selectedNote.classList.remove("selected");
    }

    selectedNote = stickyNote;
    stickyNote.classList.add("selected");

    const computedStyle = window.getComputedStyle(stickyNote);

    backgroundColorInput.value = rgbToHex(computedStyle.backgroundColor);
    borderColorInput.value = rgbToHex(computedStyle.borderColor);

  });



  stickyNote.style.left = `${noteData.x}px`;
  stickyNote.style.top = `${noteData.y}px`;
  applyGroupStyleToSticky(stickyNote);
  stickyNote.addEventListener("click", () => {
    selectStickyNote(stickyNote);
    setUiStatus(`Selected note ${stickyNote.dataset.noteId}.`);
  });

  if (noteData.backgroundColor) {
    stickyNote.style.backgroundColor = noteData.backgroundColor;
  }

  if (noteData.borderColor) {
    stickyNote.style.borderColor = noteData.borderColor;
  } 

  const textArea = document.createElement("div");
  textArea.classList.add("sticky-note-text");
  textArea.contentEditable = true;
  textArea.textContent = noteData.text;
  textArea.addEventListener("mousedown", () => {
    selectStickyNote(stickyNote);
  });
  const groupBadge = document.createElement("div");
  groupBadge.classList.add("note-group-badge");
  stickyNote.appendChild(groupBadge);

  stickyNote.appendChild(textArea);
  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "✕";
  deleteBtn.style.cssText = "position:absolute; top:-18px; right:-8px; background:red; color:white; border:none; border-radius:50%; cursor:pointer; width:18px; height:18px; font-size:11px; display:flex; align-items:center; justify-content:center; padding:0; line-height:1;";

  deleteBtn.addEventListener("click", async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/canvases/${currentCanvasId}/notes/${noteData.id}`,
        { method: "DELETE" }
      );
      if (response.ok) {
        stickyNote.remove();
      }
    } catch (error) {
      console.error("Could not delete note:", error);
    }
  });

  stickyNote.appendChild(deleteBtn);
  canvasArea.appendChild(stickyNote);

  makeStickyDraggable(stickyNote);

  textArea.addEventListener("blur", () => {
    saveStickyNote(stickyNote);
  });

  return stickyNote;
}


canvasArea.addEventListener("click", () => {
  if (selectedNote) {
    selectedNote.classList.remove("selected");
    selectedNote = null;
  }
});


backgroundColorInput.addEventListener("input", () => {
  if (!selectedNote) {
    return;
  }

  selectedNote.style.backgroundColor = backgroundColorInput.value;
  saveStickyNote(selectedNote);
});

borderColorInput.addEventListener("input", () => {
  if (!selectedNote) {
    return;
  }

  selectedNote.style.borderColor = borderColorInput.value;
  saveStickyNote(selectedNote);
});

async function saveStickyNote(stickyNote) {
  if (!currentCanvasId) {
    console.error("No canvas is currently open.");
    return;
  }

  const noteId = stickyNote.dataset.noteId;
  const text = stickyNote.querySelector(".sticky-note-text").textContent;

  const x = parseFloat(stickyNote.style.left);
  const y = parseFloat(stickyNote.style.top);

  const backgroundColor = stickyNote.style.backgroundColor;
  const borderColor = stickyNote.style.borderColor;

  try {
    const response = await fetch(
      `${API_BASE}/api/canvases/${currentCanvasId}/notes/${noteId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          text: text,
          x: x,
          y: y,
          color: 0,
          collection: stickyNote.dataset.collection || "default"
        })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error("Could not save note:", data);
      return;
    }

    console.log("Saved note:", data);

  } catch (error) {
    console.error("Connection error while saving note:", error);
  }
}


async function loadStickyNotesForCurrentCanvas() {
  if (!currentCanvasId) {
    console.error("No canvas selected.");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/api/canvases/${currentCanvasId}/notes`
    );

    const notes = await response.json();

    if (!response.ok) {
      console.error("Could not load notes:", notes);
      return;
    }

    canvasArea.innerHTML = "";

    notes.forEach(note => {
      createStickyNoteElement(note);
    });

    console.log("Loaded notes:", notes);
    await refreshGroupSelectDropdown();

  } catch (error) {
    console.error("Connection error while loading notes:", error);
  }
}


if (addStickyBtn) {
  addStickyBtn.addEventListener("click", async () => {
  if (!currentCanvasId) {
    alert("Please open or create a canvas first.");
    return;
  }

  const noteData = {
    id: Math.floor(Date.now() / 1000),// Unix timestamp in seconds to fit INT column in DB
    text: "New Sticky Note",
    x: 40,
    y: 40,
    color: 0,
    collection: "default"
  };

  try {
    const response = await fetch(
      `${API_BASE}/api/canvases/${currentCanvasId}/notes`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(noteData)
      }
    );

    const data = await response.json();

    if (!response.ok) {
      alert("Could not create sticky note: " + data.error);
      console.error("Backend error:", data);
      return;
    }

    console.log("Created sticky note:", data);

    createStickyNoteElement(noteData);

  } catch (error) {
    alert("Could not connect to backend.");
    console.error("Connection error:", error);
  }
  });
}

console.log("Frontend script loaded");

fetch(`${API_BASE}/api/health`)
  .then(response => response.json())
  .then(data => {
    console.log("Backend response:", data);
  })
  .catch(error => {
    console.error("Backend connection failed:", error);
  });

function rgbToHex(rgb) {
  const values = rgb.match(/\d+/g);

  console.log("Converting RGB to Hex:", { rgb, values });

  if (!values || values.length < 3) {
    return "#000000";
  }

  const r = parseInt(values[0]).toString(16).padStart(2, "0");
  const g = parseInt(values[1]).toString(16).padStart(2, "0");
  const b = parseInt(values[2]).toString(16).padStart(2, "0");

  return `#${r}${g}${b}`;
}
