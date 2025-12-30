mod common;

use common::{ServerProcess, start_server};
use rstest::rstest;
use torc::client::{Configuration, default_api};
use torc::models;

/// Create a workflow with a specific user
fn create_workflow_with_user(
    config: &Configuration,
    name: &str,
    user: &str,
) -> models::WorkflowModel {
    let workflow = models::WorkflowModel::new(name.to_string(), user.to_string());
    default_api::create_workflow(config, workflow).expect("Failed to create workflow")
}

// ============================================================================
// Access Group CRUD Tests
// ============================================================================

#[rstest]
fn test_create_access_group(start_server: &ServerProcess) {
    let config = &start_server.config;

    let group = models::AccessGroupModel {
        id: None,
        name: "test-group".to_string(),
        description: Some("A test access group".to_string()),
        created_at: None,
    };

    let result =
        default_api::create_access_group(config, group).expect("Failed to create access group");

    assert!(result.id.is_some());
    assert_eq!(result.name, "test-group");
    assert_eq!(result.description, Some("A test access group".to_string()));
    assert!(result.created_at.is_some());
}

#[rstest]
fn test_create_access_group_without_description(start_server: &ServerProcess) {
    let config = &start_server.config;

    let group = models::AccessGroupModel {
        id: None,
        name: "group-no-desc".to_string(),
        description: None,
        created_at: None,
    };

    let result = default_api::create_access_group(config, group)
        .expect("Failed to create access group without description");

    assert!(result.id.is_some());
    assert_eq!(result.name, "group-no-desc");
    assert!(result.description.is_none());
}

#[rstest]
fn test_get_access_group(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a group first
    let group = models::AccessGroupModel {
        id: None,
        name: "get-test-group".to_string(),
        description: Some("Group for get test".to_string()),
        created_at: None,
    };

    let created =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created.id.unwrap();

    // Now get it by ID
    let fetched =
        default_api::get_access_group(config, group_id).expect("Failed to get access group");

    assert_eq!(fetched.id, Some(group_id));
    assert_eq!(fetched.name, "get-test-group");
    assert_eq!(fetched.description, Some("Group for get test".to_string()));
}

#[rstest]
fn test_list_access_groups(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create multiple groups
    for i in 0..3 {
        let group = models::AccessGroupModel {
            id: None,
            name: format!("list-group-{}", i),
            description: Some(format!("List test group {}", i)),
            created_at: None,
        };
        default_api::create_access_group(config, group).expect("Failed to create access group");
    }

    // List all groups
    let result =
        default_api::list_access_groups(config, None, None).expect("Failed to list access groups");

    assert!(result.items.len() >= 3);
    assert!(result.total_count >= 3);

    // Verify our groups are in the list
    let names: Vec<&str> = result.items.iter().map(|g| g.name.as_str()).collect();
    assert!(names.contains(&"list-group-0"));
    assert!(names.contains(&"list-group-1"));
    assert!(names.contains(&"list-group-2"));
}

#[rstest]
fn test_list_access_groups_pagination(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create several groups
    for i in 0..5 {
        let group = models::AccessGroupModel {
            id: None,
            name: format!("page-group-{}", i),
            description: None,
            created_at: None,
        };
        let _ = default_api::create_access_group(config, group);
    }

    // Test with limit
    let page1 = default_api::list_access_groups(config, Some(0), Some(2))
        .expect("Failed to list first page");

    assert!(page1.items.len() <= 2);
    assert!(page1.offset == 0);
    assert!(page1.limit == 2);
}

#[rstest]
fn test_delete_access_group(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a group
    let group = models::AccessGroupModel {
        id: None,
        name: "delete-test-group".to_string(),
        description: Some("Group to be deleted".to_string()),
        created_at: None,
    };

    let created =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created.id.unwrap();

    // Delete it
    let deleted =
        default_api::delete_access_group(config, group_id).expect("Failed to delete access group");

    assert_eq!(deleted.id, Some(group_id));
    assert_eq!(deleted.name, "delete-test-group");

    // Verify it's gone (should return an error)
    let result = default_api::get_access_group(config, group_id);
    assert!(result.is_err(), "Deleted group should not be found");
}

// ============================================================================
// User-Group Membership Tests
// ============================================================================

#[rstest]
fn test_add_user_to_group(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a group first
    let group = models::AccessGroupModel {
        id: None,
        name: "membership-test-group".to_string(),
        description: None,
        created_at: None,
    };

    let created =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created.id.unwrap();

    // Add a user to the group
    let membership = models::UserGroupMembershipModel {
        id: None,
        user_name: "alice".to_string(),
        group_id,
        role: "member".to_string(),
        created_at: None,
    };

    let result = default_api::add_user_to_group(config, group_id, membership)
        .expect("Failed to add user to group");

    assert!(result.id.is_some());
    assert_eq!(result.user_name, "alice");
    assert_eq!(result.group_id, group_id);
    assert_eq!(result.role, "member");
}

#[rstest]
fn test_list_group_members(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a group
    let group = models::AccessGroupModel {
        id: None,
        name: "members-list-group".to_string(),
        description: None,
        created_at: None,
    };

    let created =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created.id.unwrap();

    // Add multiple users
    for user in ["bob", "carol", "dave"] {
        let membership = models::UserGroupMembershipModel {
            id: None,
            user_name: user.to_string(),
            group_id,
            role: "member".to_string(),
            created_at: None,
        };
        default_api::add_user_to_group(config, group_id, membership)
            .expect("Failed to add user to group");
    }

    // List members
    let result = default_api::list_group_members(config, group_id, None, None)
        .expect("Failed to list group members");

    assert_eq!(result.items.len(), 3);
    let names: Vec<&str> = result.items.iter().map(|m| m.user_name.as_str()).collect();
    assert!(names.contains(&"bob"));
    assert!(names.contains(&"carol"));
    assert!(names.contains(&"dave"));
}

#[rstest]
fn test_remove_user_from_group(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a group
    let group = models::AccessGroupModel {
        id: None,
        name: "remove-member-group".to_string(),
        description: None,
        created_at: None,
    };

    let created =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created.id.unwrap();

    // Add a user
    let membership = models::UserGroupMembershipModel {
        id: None,
        user_name: "eve".to_string(),
        group_id,
        role: "member".to_string(),
        created_at: None,
    };
    default_api::add_user_to_group(config, group_id, membership)
        .expect("Failed to add user to group");

    // Remove the user
    let removed = default_api::remove_user_from_group(config, group_id, "eve")
        .expect("Failed to remove user from group");

    assert_eq!(removed.user_name, "eve");

    // Verify user is no longer in the group
    let members = default_api::list_group_members(config, group_id, None, None)
        .expect("Failed to list group members");

    let names: Vec<&str> = members.items.iter().map(|m| m.user_name.as_str()).collect();
    assert!(!names.contains(&"eve"));
}

#[rstest]
fn test_list_user_groups(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create multiple groups
    let mut group_ids = Vec::new();
    for i in 0..3 {
        let group = models::AccessGroupModel {
            id: None,
            name: format!("user-groups-test-{}", i),
            description: None,
            created_at: None,
        };

        let created =
            default_api::create_access_group(config, group).expect("Failed to create access group");
        group_ids.push(created.id.unwrap());
    }

    // Add the same user to all groups
    for group_id in &group_ids {
        let membership = models::UserGroupMembershipModel {
            id: None,
            user_name: "multi-group-user".to_string(),
            group_id: *group_id,
            role: "member".to_string(),
            created_at: None,
        };
        default_api::add_user_to_group(config, *group_id, membership)
            .expect("Failed to add user to group");
    }

    // List the user's groups
    let result = default_api::list_user_groups(config, "multi-group-user", None, None)
        .expect("Failed to list user groups");

    assert!(result.items.len() >= 3);
    let names: Vec<&str> = result.items.iter().map(|g| g.name.as_str()).collect();
    assert!(names.contains(&"user-groups-test-0"));
    assert!(names.contains(&"user-groups-test-1"));
    assert!(names.contains(&"user-groups-test-2"));
}

// ============================================================================
// Workflow-Group Association Tests
// ============================================================================

#[rstest]
fn test_add_workflow_to_group(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a workflow
    let workflow = create_workflow_with_user(config, "workflow-for-group", "wf-user");
    let workflow_id = workflow.id.unwrap();

    // Create a group
    let group = models::AccessGroupModel {
        id: None,
        name: "workflow-access-group".to_string(),
        description: None,
        created_at: None,
    };

    let created_group =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created_group.id.unwrap();

    // Add workflow to group
    let association = default_api::add_workflow_to_group(config, workflow_id, group_id)
        .expect("Failed to add workflow to group");

    assert_eq!(association.workflow_id, workflow_id);
    assert_eq!(association.group_id, group_id);
    assert!(association.created_at.is_some());
}

#[rstest]
fn test_list_workflow_groups(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a workflow
    let workflow = create_workflow_with_user(config, "workflow-multi-groups", "wf-user-2");
    let workflow_id = workflow.id.unwrap();

    // Create multiple groups and add workflow to each
    for i in 0..3 {
        let group = models::AccessGroupModel {
            id: None,
            name: format!("wf-group-{}", i),
            description: None,
            created_at: None,
        };

        let created_group =
            default_api::create_access_group(config, group).expect("Failed to create access group");
        let group_id = created_group.id.unwrap();

        default_api::add_workflow_to_group(config, workflow_id, group_id)
            .expect("Failed to add workflow to group");
    }

    // List the workflow's groups
    let result = default_api::list_workflow_groups(config, workflow_id, None, None)
        .expect("Failed to list workflow groups");

    assert!(result.items.len() >= 3);
    let names: Vec<&str> = result.items.iter().map(|g| g.name.as_str()).collect();
    assert!(names.contains(&"wf-group-0"));
    assert!(names.contains(&"wf-group-1"));
    assert!(names.contains(&"wf-group-2"));
}

#[rstest]
fn test_remove_workflow_from_group(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a workflow
    let workflow = create_workflow_with_user(config, "workflow-to-remove", "wf-user-3");
    let workflow_id = workflow.id.unwrap();

    // Create a group
    let group = models::AccessGroupModel {
        id: None,
        name: "removable-wf-group".to_string(),
        description: None,
        created_at: None,
    };

    let created_group =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created_group.id.unwrap();

    // Add workflow to group
    default_api::add_workflow_to_group(config, workflow_id, group_id)
        .expect("Failed to add workflow to group");

    // Remove workflow from group
    let removed = default_api::remove_workflow_from_group(config, workflow_id, group_id)
        .expect("Failed to remove workflow from group");

    assert_eq!(removed.workflow_id, workflow_id);
    assert_eq!(removed.group_id, group_id);

    // Verify the association is gone
    let groups = default_api::list_workflow_groups(config, workflow_id, None, None)
        .expect("Failed to list workflow groups");

    let group_ids: Vec<i64> = groups.items.iter().filter_map(|g| g.id).collect();
    assert!(!group_ids.contains(&group_id));
}

// ============================================================================
// Access Check Tests
// ============================================================================

#[rstest]
fn test_check_workflow_access_owner(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a workflow owned by "owner-user"
    let workflow = create_workflow_with_user(config, "owned-workflow", "owner-user");
    let workflow_id = workflow.id.unwrap();

    // Check that the owner has access
    let result = default_api::check_workflow_access(config, workflow_id, "owner-user")
        .expect("Failed to check workflow access");

    assert!(result.has_access);
    assert_eq!(result.user_name, "owner-user");
    assert_eq!(result.workflow_id, workflow_id);
}

#[rstest]
fn test_check_workflow_access_group_member(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a workflow owned by "creator"
    let workflow = create_workflow_with_user(config, "shared-workflow", "creator");
    let workflow_id = workflow.id.unwrap();

    // Create a group
    let group = models::AccessGroupModel {
        id: None,
        name: "access-check-group".to_string(),
        description: None,
        created_at: None,
    };

    let created_group =
        default_api::create_access_group(config, group).expect("Failed to create access group");
    let group_id = created_group.id.unwrap();

    // Add a user to the group
    let membership = models::UserGroupMembershipModel {
        id: None,
        user_name: "group-member".to_string(),
        group_id,
        role: "member".to_string(),
        created_at: None,
    };
    default_api::add_user_to_group(config, group_id, membership)
        .expect("Failed to add user to group");

    // Initially, group member should NOT have access
    let no_access = default_api::check_workflow_access(config, workflow_id, "group-member")
        .expect("Failed to check workflow access");
    assert!(!no_access.has_access);

    // Add workflow to the group
    default_api::add_workflow_to_group(config, workflow_id, group_id)
        .expect("Failed to add workflow to group");

    // Now the group member should have access
    let has_access = default_api::check_workflow_access(config, workflow_id, "group-member")
        .expect("Failed to check workflow access");
    assert!(has_access.has_access);
    assert_eq!(has_access.user_name, "group-member");
}

#[rstest]
fn test_check_workflow_access_non_member(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create a workflow
    let workflow = create_workflow_with_user(config, "private-workflow", "private-owner");
    let workflow_id = workflow.id.unwrap();

    // A random user should NOT have access
    let result = default_api::check_workflow_access(config, workflow_id, "random-user")
        .expect("Failed to check workflow access");

    assert!(!result.has_access);
    assert_eq!(result.user_name, "random-user");
}
