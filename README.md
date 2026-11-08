# Golden Grove cricket scoreboard

A Raspberry Pi TV scoreboard prototype inspired by the supplied club design. **This is a demo, not a PlayHQ integration.** All scores, names and results are fictional. It does not retrieve live scores or automatically find teams.

## What remains before it can show real scores

The club has a PlayHQ public API key, but the game/fixture response schema, accessible score fields, rate limits and four team IDs have not yet been verified. The API documentation URL provided currently returns a landing page in the development environment. The example game-centre URL is not necessarily a team ID.

To find the correct identifiers, ask the association or club administrator for the organisation and team IDs, or use the documented public API endpoints once the API reference is accessible. PlayHQ notes that organisation IDs are not readily visible on its website. Do not assume the short ID in a game-centre URL is a team ID.

Before adding the integration, obtain documented endpoint paths and sanitized example responses for fixtures, games and scorecards, including pagination and field meanings. Confirm that the public API actually includes the required live data. PlayHQ documents a separate live-score webhook integration for approved integration partners. Never put the API key in source control, the browser, logs, or sample responses.

References: [PlayHQ API usage and credentials](https://support.playhq.com/hc/en-us/articles/23949453276572-How-To-Use-PlayHQ-API-s), [API documentation](https://docs.playhq.com/tech/api/playhq-external-api), and [live scoreboard integration](https://support.playhq.com/hc/en-us/articles/23976170888476-Live-Scoreboard-Integration).

## Run on a Raspberry Pi

Requires a Pi running Raspberry Pi OS with Docker Engine and the Compose plugin, and Chromium installed on the graphical desktop. The Dockerfile uses the official multi-architecture Python image; a working network connection is needed to build it.

```sh
docker compose up -d --build
```

Open `http://127.0.0.1:8080/` on the Pi. The service is bound to the Pi's loopback interface and restarts automatically after Docker starts. Check it with `docker compose ps` and `docker compose logs scoreboard`. To stop it, run `docker compose down`.

The demo is on by default and always displays a prominent **DEMO DATA** warning. To show an unconfigured state instead, set `SCOREBOARD_MODE=unconfigured` in the Compose environment and rebuild/restart with `docker compose up -d --build`. There is no API-key configuration yet because the real integration is not implemented.

### TV kiosk

On the Pi's graphical desktop, run:

```sh
chromium --kiosk --no-first-run http://127.0.0.1:8080/
```

The executable may be called `chromium-browser` on older systems. For unattended operation, add this command to your desktop session's autostart configuration (the location varies with Raspberry Pi OS and desktop version), and configure desktop auto-login and screen blanking according to your local setup. Confirm that the service and graphical session restart correctly after a reboot. The page retries if the service becomes unavailable.

## Development

Python 3.10 or later is required; no third-party packages are needed.

```sh
python3 -m scoreboard
python3 -m unittest discover -s tests -v
```

The server listens on port 8080 by default. `PORT` changes the port and `SCOREBOARD_MODE` accepts only `demo` or `unconfigured`. The browser polls the local service every 60 seconds; this is **not** a PlayHQ refresh interval.
