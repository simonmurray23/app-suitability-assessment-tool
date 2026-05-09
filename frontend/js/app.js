const API_PATH = "/api/chat";

const form        = document.getElementById("chat-form");
const input       = document.getElementById("message-input");
const submitBtn   = document.getElementById("submit-btn");
const responseArea = document.getElementById("response-area");
const responseText = document.getElementById("response-text");
const errorArea   = document.getElementById("error-area");
const errorText   = document.getElementById("error-text");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const app_name = input.value.trim();
  if (!app_name) return;

  setLoading(true);
  hide(responseArea);
  hide(errorArea);

  try {
    const res = await fetch(API_PATH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ app_name }),
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || `Request failed (${res.status})`);
      return;
    }

    responseText.textContent = data.reply;
    show(responseArea);
  } catch (err) {
    showError("Could not reach the server. Please try again.");
  } finally {
    setLoading(false);
  }
});

function setLoading(on) {
  submitBtn.disabled = on;
  submitBtn.textContent = on ? "Sending…" : "Send";
}

function show(el) { el.hidden = false; }
function hide(el) { el.hidden = true; }
function showError(msg) { errorText.textContent = msg; show(errorArea); }
