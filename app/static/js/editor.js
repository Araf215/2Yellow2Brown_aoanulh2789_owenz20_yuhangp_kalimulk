document.addEventListener("DOMContentLoaded", () => {

  // Pool area where item cards will be displayed
  const pool = document.getElementById("pool");
  // Message shown when there are no items in the pool
  const emptyState = document.getElementById("emptyState");
  // Counter that shows how many items exist
  const count = document.getElementById("count");

  // Input fields for adding an item
  const itemText = document.getElementById("itemText"); // required text/name
  const itemImg = document.getElementById("itemImg");   // optional image URL

  // Buttons for adding/clearing
  const addItemBtn = document.getElementById("addItemBtn");
  const clearFormBtn = document.getElementById("clearFormBtn");

  // Inline error message container
  const errMsg = document.getElementById("errMsg");

  const saveTierBtn = document.getElementById("saveTierBtn");

  // Each item is an object: { id, text, img }
  let items = [];

  // Show an error message to the user
  function showError(msg) {
    errMsg.style.display = "block";   // make visible
    errMsg.textContent = msg;         // set text
  }

  // Hide/clear the error message
  function clearError() {
    errMsg.style.display = "none";
    errMsg.textContent = "";
  }

  // Generate a unique ish ID for each item (time + random)
  // This helps remove the correct item later.
  function safeId() {
    return "i_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  // Rebuild the pool UI based on the current items[] array
  // (Whenever items change, we need to call render() again)
  function render() {
    // Clear all containers
    document.querySelectorAll(".tier-content, #pool")
      .forEach(c => c.querySelectorAll(".item-card").forEach(n => n.remove()));

    // Show empty message only when there are no items
    emptyState.style.display = items.length === 0 ? "block" : "none";

    // Update count text
    count.textContent = items.length.toString();

    // Create and insert a card for each item in items[]
    for (const it of items) {

      // Card container
      const card = document.createElement("div");
      card.className = "item-card";

      // If an image URL exists, create an <img> element
      if (it.img) {
        const img = document.createElement("img");
        img.src = it.img;
        img.onerror = () => img.remove();
        card.appendChild(img);
      }

      // Body container holds the text + remove button
      const body = document.createElement("div");
      body.className = "item-body";

      const text = document.createElement("div");
      text.className = "item-text";
      text.textContent = it.text;

      // Tier dropdown
      const select = document.createElement("select");
      select.className = "tier-select";

      ["unranked", "S", "A", "B", "C", "D", "F"].forEach(t => {
        const opt = document.createElement("option");
        opt.value = t;
        opt.textContent = t === "unranked" ? "Unranked" : `Tier ${t}`;
        if (it.tier === t) opt.selected = true;
        select.appendChild(opt);
      });

      select.onchange = () => {
        it.tier = select.value;
        render();
      };

      const del = document.createElement("button");
      del.className = "remove-btn";
      del.textContent = "Remove";
      del.onclick = () => {
        items = items.filter(x => x.id !== it.id);
        render();
      };

      body.append(text, select, del);
      card.appendChild(body);

      const target =
        it.tier === "unranked"
          ? pool
          : document.getElementById(`tier-${it.tier}`);

      target.appendChild(card);
    }
  }

  // Read inputs, validate, add a new item to items[], and redraw
  function addItem() {
    clearError(); // reset any old errors

    // Trim removes extra spaces at start/end
    const text = itemText.value.trim();
    const img = itemImg.value.trim();

    // require text conditional
    if (!text) {
      showError("Item text is required.");
      return;
    }

    // Add new item object into array
    items.push({ id: safeId(), text, img, tier: "unranked" });

    // Clear inputs and focus back to text box for fast entry
    itemText.value = "";
    itemImg.value = "";
    itemText.focus();

    // Redraw pool
    render();
  }

  async function saveTierList() {
    clearError();

    let title;
    if (window.editingTierListId) {
      // Editing existing - use existing title or ask for confirmation
      title = window.existingTierListTitle || "";
      const confirmed = window.confirm(`Update "${title}"?`);
      if (!confirmed) return;
    } else {
      // Creating new
      const titleInput = window.prompt("Tier list title:");
      if (titleInput === null) return;
      title = titleInput.trim();
      if (!title) {
        showError("Tier list title is required.");
        return;
      }
    }

    const tiers = { S: [], A: [], B: [], C: [], D: [], F: [] };
    for (const it of items) {
      if (it.tier === "unranked") continue;
      if (!tiers[it.tier]) tiers[it.tier] = [];
      tiers[it.tier].push({ name: it.text, image: it.img });
    }

    let rankedCount = 0;
    for (const k in tiers) rankedCount += tiers[k].length;

    if (rankedCount === 0) {
      showError("Add at least one item to a tier before saving.");
      return;
    }

    // DEBUG: Log what we're sending
    console.log("Sending data:", {
      title,
      description: window.existingTierListDescription || "",
      tiers,
      editingId: window.editingTierListId
    });

    if (saveTierBtn) saveTierBtn.disabled = true;

    try {
      const url = window.editingTierListId 
        ? `/api/tierlists/${window.editingTierListId}`
        : "/api/tierlists";
      
      const method = window.editingTierListId ? "PUT" : "POST";

      const res = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          description: window.existingTierListDescription || "",
          tiers
        })
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok || !data.ok) {
        showError(data.error || "Save failed.");
        return;
      }

      window.location.href = data.redirect || `/view?id=${data.id}`;
    } catch (e) {
      showError("Save failed.");
    } finally {
      if (saveTierBtn) saveTierBtn.disabled = false;
    }
  }

  //Event listeners

  addItemBtn.addEventListener("click", addItem);

  clearFormBtn.addEventListener("click", () => {
    itemText.value = "";
    itemImg.value = "";
    clearError();
    itemText.focus();
  });

  if (saveTierBtn) {
    saveTierBtn.addEventListener("click", saveTierList);
  }

  // Pressing Enter in either input also adds the item
  itemText.addEventListener("keydown", (e) => {
    if (e.key === "Enter") addItem();
  });

  itemImg.addEventListener("keydown", (e) => {
    if (e.key === "Enter") addItem();
  });

  // Initial draw so emptyState + count are correct on page load
  render();

  // Load existing tier list if editing
  (function loadExistingTierList() {
    // Get tier list data from template (injected by Flask)
    const tierlistDataElement = document.getElementById("tierlist-data");
    if (!tierlistDataElement) return;

    const tierlistData = JSON.parse(tierlistDataElement.textContent);
    if (!tierlistData || !tierlistData.tiers) return;

    // Store editing info
    window.editingTierListId = tierlistData.id;
    window.existingTierListTitle = tierlistData.title;
    window.existingTierListDescription = tierlistData.description || "";

    // Convert tier list data to items array
    for (const tier of tierlistData.tiers) {
      const tierName = tier.name || tier['name'];
      const tierItems = tier.items || tier['items'] || [];
      
      for (const item of tierItems) {
        items.push({
          id: safeId(),
          text: item.name || item['name'],
          img: item.image || item['image'] || "",
          tier: tierName
        });
      }
    }

    render();
  })();
});