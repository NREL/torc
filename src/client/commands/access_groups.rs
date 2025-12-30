//! Access group management commands for team-based access control

use crate::client::apis::configuration::Configuration;
use crate::client::commands::output::{print_if_json, print_json_wrapped};
use crate::client::commands::table_format::display_table_with_count;
use reqwest::StatusCode;
use serde::{Deserialize, Serialize};
use tabled::Tabled;

// ============================================================================
// Models (matching server-side models)
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessGroupModel {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<i64>,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub created_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserGroupMembershipModel {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<i64>,
    pub user_name: String,
    pub group_id: i64,
    #[serde(default = "default_role")]
    pub role: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub created_at: Option<String>,
}

fn default_role() -> String {
    "member".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowAccessGroupModel {
    pub workflow_id: i64,
    pub group_id: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub created_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListAccessGroupsResponse {
    pub items: Vec<AccessGroupModel>,
    pub offset: i64,
    pub limit: i64,
    pub total_count: i64,
    pub has_more: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListUserGroupMembershipsResponse {
    pub items: Vec<UserGroupMembershipModel>,
    pub offset: i64,
    pub limit: i64,
    pub total_count: i64,
    pub has_more: bool,
}

// ============================================================================
// Table display types
// ============================================================================

#[derive(Tabled)]
struct GroupTableRow {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Name")]
    name: String,
    #[tabled(rename = "Description")]
    description: String,
    #[tabled(rename = "Created")]
    created_at: String,
}

#[derive(Tabled)]
struct MemberTableRow {
    #[tabled(rename = "User")]
    user_name: String,
    #[tabled(rename = "Role")]
    role: String,
    #[tabled(rename = "Added")]
    created_at: String,
}

// ============================================================================
// API Client functions
// ============================================================================

fn make_request(
    config: &Configuration,
    method: reqwest::Method,
    path: &str,
) -> reqwest::blocking::RequestBuilder {
    let url = format!("{}{}", config.base_path, path);
    let mut req = config.client.request(method, &url);

    if let Some((username, password)) = &config.basic_auth {
        req = req.basic_auth(username, password.clone());
    }

    req
}

fn handle_error_response(status: StatusCode, body: &str) -> String {
    match status {
        StatusCode::NOT_FOUND => format!("Not found: {}", body),
        StatusCode::CONFLICT => format!("Conflict: {}", body),
        StatusCode::UNAUTHORIZED => "Unauthorized: Please check your credentials".to_string(),
        StatusCode::FORBIDDEN => "Forbidden: Access denied".to_string(),
        _ => format!("Error ({}): {}", status, body),
    }
}

// Group operations
fn create_group(
    config: &Configuration,
    name: &str,
    description: Option<&str>,
) -> Result<AccessGroupModel, String> {
    let group = AccessGroupModel {
        id: None,
        name: name.to_string(),
        description: description.map(|s| s.to_string()),
        created_at: None,
    };

    let resp = make_request(config, reqwest::Method::POST, "/access_groups")
        .json(&group)
        .send()
        .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

fn get_group(config: &Configuration, id: i64) -> Result<AccessGroupModel, String> {
    let resp = make_request(
        config,
        reqwest::Method::GET,
        &format!("/access_groups/{}", id),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

fn list_groups(
    config: &Configuration,
    offset: i64,
    limit: i64,
) -> Result<ListAccessGroupsResponse, String> {
    let resp = make_request(
        config,
        reqwest::Method::GET,
        &format!("/access_groups?offset={}&limit={}", offset, limit),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

fn delete_group(config: &Configuration, id: i64) -> Result<AccessGroupModel, String> {
    let resp = make_request(
        config,
        reqwest::Method::DELETE,
        &format!("/access_groups/{}", id),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

// Membership operations
fn add_user_to_group(
    config: &Configuration,
    user_name: &str,
    group_id: i64,
    role: &str,
) -> Result<UserGroupMembershipModel, String> {
    let membership = UserGroupMembershipModel {
        id: None,
        user_name: user_name.to_string(),
        group_id,
        role: role.to_string(),
        created_at: None,
    };

    let resp = make_request(
        config,
        reqwest::Method::POST,
        &format!("/access_groups/{}/members", group_id),
    )
    .json(&membership)
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

fn remove_user_from_group(
    config: &Configuration,
    user_name: &str,
    group_id: i64,
) -> Result<(), String> {
    let resp = make_request(
        config,
        reqwest::Method::DELETE,
        &format!("/access_groups/{}/members/{}", group_id, user_name),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    if status.is_success() {
        Ok(())
    } else {
        let body = resp
            .text()
            .map_err(|e| format!("Failed to read response: {}", e))?;
        Err(handle_error_response(status, &body))
    }
}

fn list_group_members(
    config: &Configuration,
    group_id: i64,
    offset: i64,
    limit: i64,
) -> Result<ListUserGroupMembershipsResponse, String> {
    let resp = make_request(
        config,
        reqwest::Method::GET,
        &format!(
            "/access_groups/{}/members?offset={}&limit={}",
            group_id, offset, limit
        ),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

fn list_user_groups(
    config: &Configuration,
    user_name: &str,
    offset: i64,
    limit: i64,
) -> Result<ListAccessGroupsResponse, String> {
    let resp = make_request(
        config,
        reqwest::Method::GET,
        &format!(
            "/users/{}/groups?offset={}&limit={}",
            user_name, offset, limit
        ),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

// Workflow-group operations
fn add_workflow_to_group(
    config: &Configuration,
    workflow_id: i64,
    group_id: i64,
) -> Result<WorkflowAccessGroupModel, String> {
    let association = WorkflowAccessGroupModel {
        workflow_id,
        group_id,
        created_at: None,
    };

    let resp = make_request(
        config,
        reqwest::Method::POST,
        &format!("/workflows/{}/access_groups/{}", workflow_id, group_id),
    )
    .json(&association)
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

fn remove_workflow_from_group(
    config: &Configuration,
    workflow_id: i64,
    group_id: i64,
) -> Result<(), String> {
    let resp = make_request(
        config,
        reqwest::Method::DELETE,
        &format!("/workflows/{}/access_groups/{}", workflow_id, group_id),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    if status.is_success() {
        Ok(())
    } else {
        let body = resp
            .text()
            .map_err(|e| format!("Failed to read response: {}", e))?;
        Err(handle_error_response(status, &body))
    }
}

fn list_workflow_groups(
    config: &Configuration,
    workflow_id: i64,
) -> Result<ListAccessGroupsResponse, String> {
    let resp = make_request(
        config,
        reqwest::Method::GET,
        &format!("/workflows/{}/access_groups", workflow_id),
    )
    .send()
    .map_err(|e| format!("Request failed: {}", e))?;

    let status = resp.status();
    let body = resp
        .text()
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if status.is_success() {
        serde_json::from_str(&body).map_err(|e| format!("Failed to parse response: {}", e))
    } else {
        Err(handle_error_response(status, &body))
    }
}

// ============================================================================
// CLI Command definitions
// ============================================================================

#[derive(clap::Subcommand)]
pub enum AccessGroupCommands {
    /// Create a new access group
    Create {
        /// Name of the group
        #[arg()]
        name: String,
        /// Description of the group
        #[arg(short, long)]
        description: Option<String>,
    },
    /// Get details of an access group
    Get {
        /// ID of the group
        #[arg()]
        id: i64,
    },
    /// List all access groups
    List {
        /// Maximum number of groups to return
        #[arg(short, long, default_value = "100")]
        limit: i64,
        /// Offset for pagination
        #[arg(short, long, default_value = "0")]
        offset: i64,
    },
    /// Delete an access group
    Delete {
        /// ID of the group to delete
        #[arg()]
        id: i64,
    },
    /// Add a user to a group
    AddUser {
        /// ID of the group
        #[arg()]
        group_id: i64,
        /// Username to add
        #[arg()]
        user_name: String,
        /// Role in the group (admin or member)
        #[arg(short, long, default_value = "member")]
        role: String,
    },
    /// Remove a user from a group
    RemoveUser {
        /// ID of the group
        #[arg()]
        group_id: i64,
        /// Username to remove
        #[arg()]
        user_name: String,
    },
    /// List members of a group
    ListMembers {
        /// ID of the group
        #[arg()]
        group_id: i64,
        /// Maximum number of members to return
        #[arg(short, long, default_value = "100")]
        limit: i64,
        /// Offset for pagination
        #[arg(short, long, default_value = "0")]
        offset: i64,
    },
    /// List groups a user belongs to
    ListUserGroups {
        /// Username
        #[arg()]
        user_name: String,
        /// Maximum number of groups to return
        #[arg(short, long, default_value = "100")]
        limit: i64,
        /// Offset for pagination
        #[arg(short, long, default_value = "0")]
        offset: i64,
    },
    /// Add a workflow to a group (grant group access)
    AddWorkflow {
        /// ID of the workflow
        #[arg()]
        workflow_id: i64,
        /// ID of the group
        #[arg()]
        group_id: i64,
    },
    /// Remove a workflow from a group (revoke group access)
    RemoveWorkflow {
        /// ID of the workflow
        #[arg()]
        workflow_id: i64,
        /// ID of the group
        #[arg()]
        group_id: i64,
    },
    /// List groups that have access to a workflow
    ListWorkflowGroups {
        /// ID of the workflow
        #[arg()]
        workflow_id: i64,
    },
}

// ============================================================================
// Command handler
// ============================================================================

pub fn handle_access_group_commands(
    config: &Configuration,
    command: &AccessGroupCommands,
    format: &str,
) {
    match command {
        AccessGroupCommands::Create { name, description } => {
            match create_group(config, name, description.as_deref()) {
                Ok(group) => {
                    if print_if_json(format, &group, "group") {
                        // JSON was printed
                    } else {
                        println!("Successfully created access group:");
                        println!("  ID: {}", group.id.unwrap_or(-1));
                        println!("  Name: {}", group.name);
                        if let Some(desc) = &group.description {
                            println!("  Description: {}", desc);
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error creating access group: {}", e);
                    std::process::exit(1);
                }
            }
        }
        AccessGroupCommands::Get { id } => match get_group(config, *id) {
            Ok(group) => {
                if print_if_json(format, &group, "group") {
                    // JSON was printed
                } else {
                    println!("Access group:");
                    println!("  ID: {}", group.id.unwrap_or(-1));
                    println!("  Name: {}", group.name);
                    if let Some(desc) = &group.description {
                        println!("  Description: {}", desc);
                    }
                    if let Some(created) = &group.created_at {
                        println!("  Created: {}", created);
                    }
                }
            }
            Err(e) => {
                eprintln!("Error getting access group: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::List { limit, offset } => match list_groups(config, *offset, *limit) {
            Ok(response) => {
                if format == "json" {
                    print_json_wrapped("groups", &response.items, "groups");
                } else if response.items.is_empty() {
                    println!("No access groups found");
                } else {
                    let rows: Vec<GroupTableRow> = response
                        .items
                        .iter()
                        .map(|g| GroupTableRow {
                            id: g.id.unwrap_or(-1),
                            name: g.name.clone(),
                            description: g.description.clone().unwrap_or_default(),
                            created_at: g.created_at.clone().unwrap_or_default(),
                        })
                        .collect();
                    display_table_with_count(&rows, "access groups");
                }
            }
            Err(e) => {
                eprintln!("Error listing access groups: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::Delete { id } => match delete_group(config, *id) {
            Ok(group) => {
                if print_if_json(format, &group, "group") {
                    // JSON was printed
                } else {
                    println!("Successfully deleted access group:");
                    println!("  ID: {}", group.id.unwrap_or(-1));
                    println!("  Name: {}", group.name);
                }
            }
            Err(e) => {
                eprintln!("Error deleting access group: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::AddUser {
            group_id,
            user_name,
            role,
        } => match add_user_to_group(config, user_name, *group_id, role) {
            Ok(membership) => {
                if print_if_json(format, &membership, "membership") {
                    // JSON was printed
                } else {
                    println!("Successfully added user to group:");
                    println!("  User: {}", membership.user_name);
                    println!("  Group ID: {}", membership.group_id);
                    println!("  Role: {}", membership.role);
                }
            }
            Err(e) => {
                eprintln!("Error adding user to group: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::RemoveUser {
            group_id,
            user_name,
        } => match remove_user_from_group(config, user_name, *group_id) {
            Ok(()) => {
                if format == "json" {
                    println!("{{\"success\": true}}");
                } else {
                    println!(
                        "Successfully removed user '{}' from group {}",
                        user_name, group_id
                    );
                }
            }
            Err(e) => {
                eprintln!("Error removing user from group: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::ListMembers {
            group_id,
            limit,
            offset,
        } => match list_group_members(config, *group_id, *offset, *limit) {
            Ok(response) => {
                if format == "json" {
                    print_json_wrapped("members", &response.items, "members");
                } else if response.items.is_empty() {
                    println!("No members found in group {}", group_id);
                } else {
                    println!("Members of group {}:", group_id);
                    let rows: Vec<MemberTableRow> = response
                        .items
                        .iter()
                        .map(|m| MemberTableRow {
                            user_name: m.user_name.clone(),
                            role: m.role.clone(),
                            created_at: m.created_at.clone().unwrap_or_default(),
                        })
                        .collect();
                    display_table_with_count(&rows, "members");
                }
            }
            Err(e) => {
                eprintln!("Error listing group members: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::ListUserGroups {
            user_name,
            limit,
            offset,
        } => match list_user_groups(config, user_name, *offset, *limit) {
            Ok(response) => {
                if format == "json" {
                    print_json_wrapped("groups", &response.items, "groups");
                } else if response.items.is_empty() {
                    println!("User '{}' is not a member of any groups", user_name);
                } else {
                    println!("Groups for user '{}':", user_name);
                    let rows: Vec<GroupTableRow> = response
                        .items
                        .iter()
                        .map(|g| GroupTableRow {
                            id: g.id.unwrap_or(-1),
                            name: g.name.clone(),
                            description: g.description.clone().unwrap_or_default(),
                            created_at: g.created_at.clone().unwrap_or_default(),
                        })
                        .collect();
                    display_table_with_count(&rows, "groups");
                }
            }
            Err(e) => {
                eprintln!("Error listing user groups: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::AddWorkflow {
            workflow_id,
            group_id,
        } => match add_workflow_to_group(config, *workflow_id, *group_id) {
            Ok(association) => {
                if print_if_json(format, &association, "association") {
                    // JSON was printed
                } else {
                    println!("Successfully added workflow to group:");
                    println!("  Workflow ID: {}", association.workflow_id);
                    println!("  Group ID: {}", association.group_id);
                }
            }
            Err(e) => {
                eprintln!("Error adding workflow to group: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::RemoveWorkflow {
            workflow_id,
            group_id,
        } => match remove_workflow_from_group(config, *workflow_id, *group_id) {
            Ok(()) => {
                if format == "json" {
                    println!("{{\"success\": true}}");
                } else {
                    println!(
                        "Successfully removed workflow {} from group {}",
                        workflow_id, group_id
                    );
                }
            }
            Err(e) => {
                eprintln!("Error removing workflow from group: {}", e);
                std::process::exit(1);
            }
        },
        AccessGroupCommands::ListWorkflowGroups { workflow_id } => {
            match list_workflow_groups(config, *workflow_id) {
                Ok(response) => {
                    if format == "json" {
                        print_json_wrapped("groups", &response.items, "groups");
                    } else if response.items.is_empty() {
                        println!("Workflow {} is not associated with any groups", workflow_id);
                    } else {
                        println!("Groups with access to workflow {}:", workflow_id);
                        let rows: Vec<GroupTableRow> = response
                            .items
                            .iter()
                            .map(|g| GroupTableRow {
                                id: g.id.unwrap_or(-1),
                                name: g.name.clone(),
                                description: g.description.clone().unwrap_or_default(),
                                created_at: g.created_at.clone().unwrap_or_default(),
                            })
                            .collect();
                        display_table_with_count(&rows, "groups");
                    }
                }
                Err(e) => {
                    eprintln!("Error listing workflow groups: {}", e);
                    std::process::exit(1);
                }
            }
        }
    }
}
