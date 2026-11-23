const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const chips = document.getElementById("chips");
const badge = document.getElementById("badge");

function addMsg(text, who) {
  const wrap = document.createElement("div");
  wrap.className = "msg " + who;
  const b = document.createElement("div");
  b.className = "bubble";
  b.textContent = text;
  wrap.appendChild(b);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return b;
}

function addSources(bubble, sources) {
  if (!sources || !sources.length) return;
  const d = document.createElement("details");
  d.className = "sources";
  const s = document.createElement("summary");
  s.textContent = "Sources (" + sources.length + ")";
  d.appendChild(s);
  sources.forEach(x => {
    const el = document.createElement("div");
    el.className = "src";
    const t = document.createElement("b");
    t.textContent = x.title + " - match " + x.score;
    el.appendChild(t);
    el.appendChild(document.createTextNode(x.snippet));
    d.appendChild(el);
  });
  bubble.appendChild(d);
}

async function ask(q) {
  q = q.trim();
  if (!q) return;
  if (chips) chips.style.display = "none";
  addMsg(q, "user");
  input.value = "";
  sendBtn.disabled = true;
  const bot = addMsg("", "bot");
  bot.innerHTML = '<span class="typing"><i></i><i></i><i></i></span>';
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: q})
    });
    const data = await r.json();
    bot.textContent = data.answer || data.error || "Something went wrong.";
    addSources(bot, data.sources);
  } catch (e) {
    bot.textContent = "Could not reach the server. Is Flask running?";
  }
  sendBtn.disabled = false;
  input.focus();
  chat.scrollTop = chat.scrollHeight;
}

sendBtn.onclick = () => ask(input.value);
input.addEventListener("keydown", e => { if (e.key === "Enter") ask(input.value); });
document.querySelectorAll(".chip").forEach(c => c.onclick = () => ask(c.textContent));

fetch("/api/health").then(r => r.json()).then(h => {
  badge.textContent = h.llm ? "Claude + RAG" : "Offline RAG";
}).catch(() => { badge.textContent = "offline"; });
