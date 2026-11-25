"""Edit the client IDs here once; no PowerShell environment variables needed."""

# Existing client for read-only UI checks.
READ_ONLY_CLIENT_ID = "SENTINELE7CE963CAACEA23"

# Enter a DIFFERENT disposable, already-onboarded Individual client ID.
WRITE_CLIENT_ID = ""

# Enter an Individual client ID with at least one Connected Party card.
CONNECTED_PARTY_CLIENT_ID = ""

# Explicit safety opt-in. Set True only after confirming WRITE_CLIENT_ID
# belongs to a disposable client whose screening records may be changed.
ALLOW_SCREENING_CHANGES = False
