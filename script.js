const log = document.getElementById("log");
const form = document.getElementById("entry-form");
const input = document.getElementById("entry-input");
const matchNote = document.getElementById("match-note");
const suggestions = document.getElementById("suggestions");

function addEntry(role, text) {
  const entry = document.createElement("div");
  entry.className = `entry ${role}`;

  const stamp = document.createElement("div");
  stamp.className = "stamp";
  stamp.textContent = role === "user" ? "You" : "Field Book";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  entry.appendChild(stamp);
  entry.appendChild(bubble);
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
}

async function sendMessage(message) {
  addEntry("user", message);
  matchNote.textContent = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();

    addEntry("bot", data.answer);

    if (data.matched_question) {
      matchNote.textContent = `Matched: "${data.matched_question}" (similarity ${data.score})`;
    } else {
      matchNote.textContent = "";
    }
  } catch (err) {
    addEntry("bot", "Something went wrong reaching the server. Is app.py running?");
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  sendMessage(message);
});

suggestions.addEventListener("click", (e) => {
  const chip = e.target.closest(".row-chip");
  if (!chip) return;
  sendMessage(chip.dataset.q);
});
