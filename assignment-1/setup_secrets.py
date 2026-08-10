"""
One-time setup script: creates the Databricks secret scope and stores the
Lakebase URL. Run this locally (with the Databricks CLI configured) or
from a notebook - never commit the resulting secret value anywhere.

Usage:
    python setup_secrets.py
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

# w.secrets.create_scope(scope="support_ticket_app")
w.secrets.put_secret(
    scope="support_ticket_app",
    key="lakebase-url",
    string_value=getpass.getpass("Paste your Lakebase URL: ")
)

w.secrets.put_acl(
    scope="support_ticket_app",
    principal="users",
    permission=workspace.AclPermission.READ,
)
