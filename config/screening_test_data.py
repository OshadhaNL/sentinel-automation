
"""
Centralized test data for Individual Screening automation.

Configure client IDs here instead of entering them
through PowerShell environment variables.
"""

# ---------------------------------------
# READ-ONLY SCREENING CLIENT
# ---------------------------------------

# Existing Individual Profile used for UI,
# navigation, validation and negative tests.

READ_ONLY_CLIENT_ID = "SENTINELE7CE963CAACEA23"


# ---------------------------------------
# WRITE-OPERATION SCREENING CLIENT
# ---------------------------------------

# Enter the ID of a dedicated disposable
# Individual Profile.
#
# This client may be modified by automation.

WRITE_CLIENT_ID = "SENTINEL2343E1F1DFA0917"


# ---------------------------------------
# CONNECTED-PARTY TEST CLIENT
# ---------------------------------------

# Enter an Individual Profile ID that has
# at least one Connected Party record.

CONNECTED_PARTY_CLIENT_ID = "SENTINEL82A277827294F7C"


# ---------------------------------------
# WRITE-OPERATION PERMISSION
# ---------------------------------------

# Set True only when the write client is
# dedicated to automation and may be modified.

ALLOW_SCREENING_CHANGES = True
