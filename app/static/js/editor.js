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

    // Remove old item cards so we can redraw cleanly
    pool.querySelectorAll(".item-card").forEach(n => n.remove());

    // Show empty message only when there are no items
    emptyState.style.display = items.length === 0 ? "block" : "none";

    // Update count text
    count.textContent = items.length.toString();

    // Create and insert a card for each item in items[]
    for (const it of items) {

      // Card container
      const card = document.createElement("div");
      card.className = "item-card";
      // Store item ID in HTML as a data attribute (gonna use this for debugging/drag-drop later)
      card.dataset.itemId = it.id;

      // If an image URL exists, create an <img> element
      if (it.img) {
        const img = document.createElement("img");
        img.src = it.img;
        img.alt = it.text;
        img.loading = "lazy"; // loads image only when needed (so its not laggy)
        // If the image link is broken, remove the image element
        img.onerror = () => img.remove();
        card.appendChild(img);
      }

      // Body container holds the text + remove button
      const body = document.createElement("div");
      body.className = "item-body";

      const text = document.createElement("div");
      text.className = "item-text";
      text.textContent = it.text;

      // Remove button deletes this item from items[] then re renders
      const del = document.createElement("button");
      del.className = "remove-btn";
      del.type = "button";
      del.textContent = "Remove";
      del.onclick = () => {
        // Keep all items except the one being removed
        items = items.filter(x => x.id !== it.id);
        render(); // redraw UI after update
      };

      // Put text and button into body
      body.appendChild(text);
      body.appendChild(del);

      // Put body into card, and card into pool
      card.appendChild(body);
      pool.appendChild(card);
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
    items.push({ id: safeId(), text, img });

    // Clear inputs and focus back to text box for fast entry
    itemText.value = "";
    itemImg.value = "";
    itemText.focus();

    // Redraw pool
    render();
  }

  //Event listeners

  addItemBtn.addEventListener("click", addItem);

  clearFormBtn.addEventListener("click", () => {
    itemText.value = "";
    itemImg.value = "";
    clearError();
    itemText.focus();
  });

  // Pressing Enter in either input also adds the item
  itemText.addEventListener("keydown", (e) => {
    if (e.key === "Enter") addItem();
  });

  itemImg.addEventListener("keydown", (e) => {
    if (e.key === "Enter") addItem();
  });

  // Initial draw so emptyState + count are correct on page load
  render();
});
