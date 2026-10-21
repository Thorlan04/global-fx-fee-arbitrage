# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Architecture & Design Principles

The `global-fx-fee-arbitrage` platform is designed with a **privacy-first and zero-custody** architecture:
1. **Client-Side Calculations:** All currency conversions, fee deductions, and mathematical simulations run entirely within the user's browser in vanilla JavaScript. No user inputs (amounts, corridors, IP addresses) are transmitted or stored on any server.
2. **Public Verified Data:** Rates are sourced exclusively from the official European Central Bank (ECB) XML reference feed over HTTPS.
3. **Least Privilege CI/CD:** GitHub Actions workflows operate with fine-grained scoped permissions (`contents: write` restricted only to rate sync jobs, and `pages: write` for GitHub Pages). Pull requests do not have access to deployment tokens.
4. **Zero Third-Party Tracking:** No invasive trackers, third-party analytics pixels, or cookies are embedded on the site.

## Reporting a Vulnerability

If you discover a security vulnerability within this repository, please do **NOT** open a public issue.

Instead, please report it through one of the following channels:
1. **GitHub Security Advisory:** Submit a private vulnerability report via the [Security Advisory Tab](https://github.com/Thorlan04/global-fx-fee-arbitrage/security/advisories/new).
2. **Direct Contact:** Contact the repository maintainer through GitHub profile contact options.

We commit to:
- Acknowledge receipt of the report within 48 hours.
- Provide a patch and remediation roadmap within 7 days.
- Credit researchers responsibly upon disclosure.
