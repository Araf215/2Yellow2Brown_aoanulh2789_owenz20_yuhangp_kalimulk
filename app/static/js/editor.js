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

      let  user_tiers = []

      document.getElementById("put_html_form_ID_here").addEventListener('submit', function(event)) {
	  const formData = new FormData(this)
	  const url = formData.get('url')

	  fetch(url).then(response => {
	      if (!response.ok) {
		  throw new Error('shid is cooked: ' + response.statusText)
	      }
	      user_tiers = response.json()
      }

      // replace below array with user_tiers; make sure user_tiers = (user_tiers.empty ? default : user_tiers)
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
