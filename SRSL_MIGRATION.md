# AUDIOANALYSISX1 licence scope and migration — 2026-10-17

**Scope:** SWORD-owned first-party source code not independently licensed elsewhere in distributions adopting this release is offered under [SRSL-1.1](LICENSE). The exact previously distributed [SRSL-1.0 text](LICENSES/SRSL-1.0.txt) is archived. This publication does not revoke any previously granted permissions.

**Existing inconsistent metadata:** `electron_app/package.json` advertises `"license": "MIT"`. That declaration is left unchanged; components independently and validly licensed under MIT retain those rights and are not retroactively restricted by the repository root SRSL. Determine code ownership, earlier grants, and any intended prospective package relicensing separately before modifying the Electron package. Dependencies, included assets and Electron itself retain their own terms.

The first-party SRSL grant permits enumerated non-commercial uses and reserves commercial and source model-development rights subject to mandatory statutory exceptions. Fifty percent profit participation is a proposed negotiated commercial term, not an automatic debt for infringement.

This change does not modify executable code, audio-processing behaviour, security, activation, or telemetry. Legal review is needed to reconcile historic packaging representations where commercial enforcement is contemplated.
