document.addEventListener("DOMContentLoaded", () => {
    console.log("ByteBites Quest System Loaded!");

    document.querySelectorAll(".vendor-card").forEach(card => {
        card.addEventListener("click", () => {
            card.classList.add("quest-selected");
        });
    });
});
