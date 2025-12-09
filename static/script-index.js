const modal = document.getElementById("registerModal");
const openBtn = document.querySelector(".register-link a");
const closeBtn = document.querySelector(".close-btn");

openBtn.addEventListener("click", (e) => {
    e.preventDefault(); // prevent default link behavior
    modal.style.display = "block";
});

closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
    removeShowRegisterFromURL();
});

// Close modal if user clicks outside the box
window.addEventListener("click", (e) => {
    if (e.target == modal) {
        modal.style.display = "none";
        removeShowRegisterFromURL();
    }
});

// Function to remove ?show_register=1 and flash from URL, so the messages wont appear again
function removeShowRegisterFromURL() {
    if (window.history.replaceState) {
        const url = new URL(window.location);
        url.searchParams.delete("show_register");
        window.history.replaceState({}, document.title, url);

        const flash = document.querySelector(".flash-messages");
        if (flash) flash.style.display = "none";
    }
}
