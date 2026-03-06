# QRDrop

A lightweight, ephemeral local chat tool for transferring messages and files between two devices without accounts, logs, or persistent data. Initiate a session, scan the QR code on a second device, exchange what you need, and leave nothing behind.

## How it works

1. Open QRDrop on one device and create a session
2. Scan the generated QR code on a second device
3. Chat or transfer what you need
4. Close the session — no logs, no user records, no trace

Sessions exist only in memory. The only state persisted at any point is temporary session metadata, which is discarded when the session ends.

## Architecture

**Backend:** Python / FastAPI / WebSockets
**Frontend:** Vue 3 (Composition API) / TypeScript / Tailwind CSS

Communication is handled over WebSockets. The backend manages session state in memory; the frontend connects via WebSocket on session join and disconnects cleanly on exit.

## Security model

QRDrop is designed for local network use:

- **No persistence:** no database, no chat logs, no user accounts
- **In-memory only:** session state lives only for the duration of the session
- **Transport:** currently uses `ws://` — suitable for trusted local networks. `wss://` support is planned for any deployment beyond localhost
- **Threat model:** QRDrop is not designed to resist a sophisticated adversary. It is designed to leave nothing behind after use.

## Status

Active development. Core functionality (session creation, QR join flow, real-time messaging) is working. Planned additions:

- File transfer support
- `wss://` / TLS support for non-local deployment
- Packaging and installation story

## Setup

_Installation instructions to come once packaging is finalized. The backend is a standard FastAPI app, and the frontend is a Vite/Vue project — both runnable in the usual ways in the meantime._

## License

GPL v3 — see [LICENSE](LICENSE)
