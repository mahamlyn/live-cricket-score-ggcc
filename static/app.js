"use strict";

const games = document.getElementById("games");
const notice = document.getElementById("notice");
const footer = document.getElementById("footer");
let showingDemo = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = text;
  return node;
}

function renderGame(game) {
  const card = element("article", "match", "");
  const header = element("header", "match-header", "");
  header.append(element("div", "grade", game.grade), element("div", "fixture", game.fixture));
  const teams = element("div", "teams", "");
  for (const team of game.teams) {
    const side = element("section", "team", "");
    side.append(element("div", "team-name", `${team.name} - ${team.score}`));
    if (team.players.length) {
      for (const player of team.players) side.append(element("div", "player", player));
    } else {
      side.append(element("div", "missing", "Player details unavailable"));
    }
    teams.append(side);
  }
  card.append(header, teams, element("div", "match-status", game.status));
  return card;
}

async function refresh() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch("/api/scoreboard", { cache: "no-store", signal: controller.signal });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Server error (${response.status})`);
    if (data.mode !== "demo" || !Array.isArray(data.games) || data.games.length !== 4) {
      throw new Error("Unrecognized scoreboard data");
    }
    const cards = data.games.map(renderGame);
    games.replaceChildren(...cards);
    showingDemo = true;
    notice.className = "notice";
    notice.textContent = "DEMO DATA — NOT LIVE OR CONNECTED TO PLAYHQ";
    footer.textContent = "Fictional example scores and players. PlayHQ integration not yet implemented.";
  } catch (error) {
    notice.className = "notice error";
    notice.textContent = showingDemo
      ? "DEMO DATA — NOT LIVE; scoreboard unavailable"
      : "SCOREBOARD UNAVAILABLE";
    footer.textContent = `Unable to load scoreboard: ${error.message}. Retrying automatically.`;
    if (!games.children.length) games.append(element("p", "empty", "Scoreboard unavailable"));
  } finally {
    clearTimeout(timeout);
  }
}

refresh();
setInterval(refresh, 60000);
