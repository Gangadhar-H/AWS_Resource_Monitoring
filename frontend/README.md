# Frontend (React + Vite)

Pages: Home (`/`), Resources (`/resources`), Resource detail (`/resources/:type/:id`), Savings (`/savings`), About (`/about`).

## How to extend
| I want to... | Change |
|---|---|
| Add a page | create `src/pages/X.jsx`, add a `<Route>` in `App.jsx`, add a menu entry in `config/navigation.js` |
| Support a new resource type (RDS, S3...) | add one entry in `config/resourceTypes.js` (label, colour, card facts, detail fields). Cards, filters and the detail page pick it up automatically. The backend needs a collector + rule + price for it |
| Add a status | add it in `config/statuses.js` |
| Add shared data (history, settings) | extend `context/ScanContext.jsx` and `services/api.js` |

Filters on the Resources page live in the URL (`?type=ebs&status=unused&q=text&sort=cost`), so views can be bookmarked.
