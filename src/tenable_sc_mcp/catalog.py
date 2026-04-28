from __future__ import annotations

from dataclasses import dataclass


DOCS_BASE_URL = "https://docs.tenable.com/security-center/api"


@dataclass(frozen=True)
class ApiResource:
    name: str
    path: str
    docs: str
    description: str
    admin_or_director: bool = False


def _doc(page: str) -> str:
    return f"{DOCS_BASE_URL}/{page}.htm"


# Resource names and documentation pages are taken from the Tenable.sc API index.
# Tenable.sc RBAC is enforced by the API identity used to call these endpoints.
API_RESOURCES: tuple[ApiResource, ...] = (
    ApiResource("Accept Risk Rule", "acceptRiskRule", _doc("Accept-Risk-Rule"), "Accept risk rule management."),
    ApiResource("Agent Group", "agentGroup", _doc("Agent-Group"), "Agent group management."),
    ApiResource("Agent Results Sync", "agentResultsSync", _doc("Agent-Results-Sync"), "Agent result synchronization operations."),
    ApiResource("Agent Scan", "agentScan", _doc("Agent-Scan"), "Agent scan operations."),
    ApiResource("Alert", "alert", _doc("Alert"), "Alert management."),
    ApiResource("Analysis", "analysis", _doc("Analysis"), "Vulnerability, event, and analysis queries."),
    ApiResource("ARC", "arc", _doc("ARC"), "Assurance Report Card management."),
    ApiResource("ARC Template", "arcTemplate", _doc("ARC-Template"), "ARC template management."),
    ApiResource("Asset", "asset", _doc("Asset"), "Asset list management."),
    ApiResource("Asset Template", "assetTemplate", _doc("Asset-Template"), "Asset template management."),
    ApiResource("Attribute Set", "attributeSet", _doc("Attribute-Set"), "Attribute set management."),
    ApiResource("AuditFile", "auditFile", _doc("AuditFile"), "Audit file management."),
    ApiResource("AuditFile Template", "auditFileTemplate", _doc("AuditFile-Template"), "Audit file template management."),
    ApiResource("Bulk", "bulk", _doc("Bulk"), "Bulk API operations."),
    ApiResource("Configuration", "configuration", _doc("Configuration"), "System configuration operations.", True),
    ApiResource("Configuration Section", "configurationSection", _doc("Configuration-Section"), "Configuration section operations.", True),
    ApiResource("Credential", "credential", _doc("Credential"), "Credential management."),
    ApiResource("Current Organization", "currentOrganization", _doc("Current-Organization"), "Current organization details."),
    ApiResource("Current User", "currentUser", _doc("Current-User"), "Current API user details and permissions."),
    ApiResource("Custom Plugins", "customPlugins", _doc("Custom-Plugins"), "Custom plugin management."),
    ApiResource("Dashboard Component", "dashboardComponent", _doc("Dashboard-Component"), "Dashboard component management."),
    ApiResource("Dashboard Tab", "dashboardTab", _doc("Dashboard-Tab"), "Dashboard tab management."),
    ApiResource("Dashboard Template", "dashboardTemplate", _doc("Dashboard-Template"), "Dashboard template management."),
    ApiResource("Device Information", "deviceInformation", _doc("Device-Information"), "Device information queries."),
    ApiResource("Director Insights", "directorInsights", _doc("Director-Insights"), "Director insights operations.", True),
    ApiResource("Director Organization", "directorOrganization", _doc("Director-Organization"), "Director organization operations.", True),
    ApiResource("Director Repository", "directorRepository", _doc("Director-Repository"), "Director repository operations.", True),
    ApiResource("Director Scan", "directorScan", _doc("Director-Scan"), "Director scan operations.", True),
    ApiResource("Director Scanner", "directorScanner", _doc("Director-Scanner"), "Director scanner operations.", True),
    ApiResource("Director Scan Policy", "directorScanPolicy", _doc("Director-Scan-Policy"), "Director scan policy operations.", True),
    ApiResource("Director Scan Result", "directorScanResult", _doc("Director-Scan-Result"), "Director scan result operations.", True),
    ApiResource("Director Scan Zone", "directorScanZone", _doc("Director-Scan-Zone"), "Director scan zone operations.", True),
    ApiResource("Director System", "directorSystem", _doc("Director-System"), "Director system operations.", True),
    ApiResource("Director User", "directorUser", _doc("Director-User"), "Director user operations.", True),
    ApiResource("Feed", "feed", _doc("Feed"), "Feed status and management."),
    ApiResource("File", "file", _doc("File"), "File upload/download metadata operations."),
    ApiResource("Freeze Window", "freezeWindow", _doc("Freeze-Window"), "Freeze window management."),
    ApiResource("Group", "group", _doc("Group"), "Group management."),
    ApiResource("Hosts", "hosts", _doc("Hosts"), "Host lookup and host-related data."),
    ApiResource("Job", "job", _doc("Job"), "Job status and job management."),
    ApiResource("LCE", "lce", _doc("LCE"), "Log Correlation Engine management."),
    ApiResource("LCE Client", "lceClient", _doc("LCE-Client"), "LCE client management."),
    ApiResource("LCE Policy", "lcePolicy", _doc("LCE-Policy"), "LCE policy management."),
    ApiResource("LDAP", "ldap", _doc("LDAP"), "LDAP configuration management.", True),
    ApiResource("LicenseInfo", "licenseInfo", _doc("LicenseInfo"), "License information."),
    ApiResource("Lumin", "lumin", _doc("Lumin"), "Lumin/exposure score operations."),
    ApiResource("MDM", "mdm", _doc("MDM"), "Mobile device management operations."),
    ApiResource("Notification", "notification", _doc("Notification"), "Notification management."),
    ApiResource("Organization", "organization", _doc("Organization"), "Organization management.", True),
    ApiResource("Organization Security Manager", "organizationSecurityManager", _doc("Organization-Security-Manager"), "Organization security manager management.", True),
    ApiResource("Organization User", "organizationUser", _doc("Organization-User"), "Organization user management.", True),
    ApiResource("Passive Scanner (NNM)", "passiveScanner", _doc("Passive-Scanner"), "Passive scanner/NNM management."),
    ApiResource("Plugin", "plugin", _doc("Plugin"), "Plugin queries."),
    ApiResource("Plugin Family", "pluginFamily", _doc("Plugin-Family"), "Plugin family queries."),
    ApiResource("Publishing Site", "publishingSite", _doc("Publishing-Site"), "Publishing site management."),
    ApiResource("Query", "query", _doc("Query"), "Saved query management."),
    ApiResource("Recast Risk Rule", "recastRiskRule", _doc("Recast-Risk-Rule"), "Recast risk rule management."),
    ApiResource("Report", "report", _doc("Report"), "Report operations."),
    ApiResource("Report Definition", "reportDefinition", _doc("Report-Definition"), "Report definition management."),
    ApiResource("Report Image", "reportImage", _doc("Report-Image"), "Report image management."),
    ApiResource("Report Template", "reportTemplate", _doc("Report-Template"), "Report template management."),
    ApiResource("Repository", "repository", _doc("Repository"), "Repository management."),
    ApiResource("Role", "role", _doc("Role"), "Role and permission metadata."),
    ApiResource("SAML", "saml", _doc("SAML"), "SAML configuration management.", True),
    ApiResource("Scanner", "scanner", _doc("Scanner"), "Scanner management."),
    ApiResource("Scan", "scan", _doc("Scan"), "Scan policy instance management and launch actions."),
    ApiResource("Scan Policy", "scanPolicy", _doc("Scan-Policy"), "Scan policy management."),
    ApiResource("Scan Policy Templates", "scanPolicyTemplate", _doc("Scan-Policy-Templates"), "Scan policy template queries."),
    ApiResource("Scan Result", "scanResult", _doc("Scan-Result"), "Scan result queries and actions."),
    ApiResource("Scan Zone", "scanZone", _doc("Scan-Zone"), "Scan zone management."),
    ApiResource("Sensor Proxy", "sensorProxy", _doc("Sensor-Proxy"), "Sensor proxy management."),
    ApiResource("Solutions", "solutions", _doc("Solutions"), "Solution/remediation queries."),
    ApiResource("SSHKey", "sshKey", _doc("SSHKey"), "SSH key management."),
    ApiResource("Status", "status", _doc("Status"), "Server status."),
    ApiResource("Style", "style", _doc("Style"), "Report style management."),
    ApiResource("Style Family", "styleFamily", _doc("StyleFamily"), "Report style family management."),
    ApiResource("System", "system", _doc("System"), "System operations.", True),
    ApiResource("Tenable.sc Instance", "tenableScInstance", _doc("Tenable.sc-Instance"), "Tenable.sc instance management.", True),
    ApiResource("TES Admin Roles", "tesAdminRoles", _doc("TES-Admin-Roles"), "Tenable Exposure Services admin role metadata.", True),
    ApiResource("TES User Permissions", "tesUserPermissions", _doc("TES-User-Permissions"), "Tenable Exposure Services user permission metadata."),
    ApiResource("Ticket", "ticket", _doc("Ticket"), "Ticket management."),
    ApiResource("Token", "token", _doc("Token"), "Token/session operations."),
    ApiResource("User", "user", _doc("User"), "User management.", True),
    ApiResource("WAS Scan", "wasScan", _doc("WAS-Scan"), "Web application scan operations."),
    ApiResource("WAS Scanner", "wasScanner", _doc("WAS-Scanner"), "Web application scanner operations."),
)

RESOURCE_BY_PATH = {resource.path: resource for resource in API_RESOURCES}


def catalog_as_dict() -> list[dict[str, object]]:
    return [
        {
            "name": resource.name,
            "path": resource.path,
            "rest_path": f"/rest/{resource.path}",
            "docs": resource.docs,
            "description": resource.description,
            "admin_or_director": resource.admin_or_director,
        }
        for resource in API_RESOURCES
    ]
