# Amplifier Client Ledger

Served at https://athemventures.com/amplifierdashboard/ (GitHub Pages, this repo).

- `index.html`: the built page. Holds no client data. It signs in with Google and reads the `opportunities` collection in Firebase project `amplifier-ledger` (Firestore, nam5).
- `src/app.js`, `src/app.css`: source inlined into `index.html`.
- Access is enforced by Firestore security rules: only mehta@helix.harvard7.net and amit@amplifierhealth.com, signed in with a verified Google account, can read or write. The Firebase web config in the page is a public identifier, not a secret.
- Authorized sign-in domains: athemventures.com, www.athemventures.com.
- Data: the Notion database "Amplifier Opportunities" is synced nightly from Gmail, Slack (#customers-discovery-insights) and Notion. GTM team = surfaced in Slack with no email thread yet.
