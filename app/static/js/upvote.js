// gets the html element clicked, async runs asynchronously to also allow await 
document.addEventListener('click', async (e) => {
    // returns if the thingy clicked isn't the voting buttons
    if(!e.target.classList.contains("upvote") && !e.target.classList.contains("downvote")){
        return;
    }

    const votingDiv = e.target.closest(".voting");
    const voteCountSpan = votingDiv.queryselector(".votecount");
    const tierlistID = votingDiv.dataset.tierlistid;
    const value = e.target.classList.contains("upvote") ? 1 : -1;

    // post request to update voting count, sends json string data to flask /dashboard route
    const response = await fetch("/dashboard", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            tierlist_id: tierlistID,
            value: value
        })
    });

    // gets the returned data from flask and parses it through json 
    const data = await response.json();
    voteCountSpan.textContent = data.upvotes;

});