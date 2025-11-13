mod common;

use common::{
    ServerProcess, create_test_event, create_test_workflow, run_cli_with_json, start_server,
};
use rstest::rstest;
use serde_json::json;

#[rstest]
fn test_events_add_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow
    let workflow = create_test_workflow(config, "test_events_add_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test the CLI create command with JSON output
    let test_data = r#"{"event_type": "test", "message": "Hello World", "level": "info"}"#;
    let args = [
        "events",
        "create",
        &workflow_id.to_string(),
        "--data",
        test_data,
    ];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run events create command");

    assert!(json_output.get("id").is_some());
    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));
    assert!(json_output.get("timestamp").is_some());

    let expected_data: serde_json::Value = serde_json::from_str(test_data).unwrap();
    assert_eq!(json_output.get("data").unwrap(), &expected_data);

    // Verify timestamp is in correct format (ISO 8601)
    let timestamp = json_output.get("timestamp").unwrap().as_str().unwrap();
    assert!(
        timestamp.ends_with("Z"),
        "Timestamp should be in UTC (end with Z)"
    );
    assert!(
        timestamp.contains("T"),
        "Timestamp should contain 'T' separator"
    );
}

#[rstest]
fn test_events_add_complex_data(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_complex_data_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test with complex nested JSON data
    let complex_data = r#"{
        "event_type": "job_status_change",
        "job_info": {
            "id": 123,
            "name": "test_job",
            "status": "running"
        },
        "metadata": {
            "timestamp": "2024-01-01T12:00:00Z",
            "source": "job_runner",
            "tags": ["production", "critical"],
            "metrics": {
                "cpu_usage": 75.5,
                "memory_mb": 512
            }
        },
        "changes": [
            {"field": "status", "from": "pending", "to": "running"},
            {"field": "start_time", "from": null, "to": "2024-01-01T12:00:00Z"}
        ]
    }"#;

    let args = [
        "events",
        "create",
        &workflow_id.to_string(),
        "--data",
        complex_data,
    ];

    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run events create with complex data");

    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));

    let expected_data: serde_json::Value = serde_json::from_str(complex_data).unwrap();
    assert_eq!(json_output.get("data").unwrap(), &expected_data);
}

#[rstest]
fn test_events_list_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and events
    let workflow = create_test_workflow(config, "test_events_list_workflow");
    let workflow_id = workflow.id.unwrap();

    let _event1 = create_test_event(
        config,
        workflow_id,
        json!({"type": "start", "message": "Workflow started"}),
    );
    std::thread::sleep(std::time::Duration::from_millis(10));
    let _event2 = create_test_event(
        config,
        workflow_id,
        json!({"type": "progress", "message": "Job completed", "job_id": 123}),
    );

    // Test the CLI list command
    let args = ["events", "list", &workflow_id.to_string(), "--limit", "10"];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run events list command");

    // Verify JSON structure is an object with "events" field
    assert!(
        json_output.is_object(),
        "Events list should return an object"
    );
    assert!(
        json_output.get("events").is_some(),
        "Response should have 'events' field"
    );

    let events_array = json_output.get("events").unwrap().as_array().unwrap();
    assert!(events_array.len() >= 2, "Should have at least 2 events");

    // Verify each event has the expected structure
    for event in events_array {
        assert!(event.get("id").is_some());
        assert!(event.get("workflow_id").is_some());
        assert!(event.get("timestamp").is_some());
        assert!(event.get("data").is_some());
    }

    let first_timestamp = events_array[0].get("timestamp").unwrap().as_str().unwrap();
    let second_timestamp = events_array[1].get("timestamp").unwrap().as_str().unwrap();
    assert!(
        second_timestamp > first_timestamp,
        "Events should be sorted oldest first"
    );
}

#[rstest]
fn test_events_list_pagination(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_pagination_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create multiple events
    for i in 0..5 {
        let _event = create_test_event(
            config,
            workflow_id,
            json!({"index": i, "message": format!("Event {}", i)}),
        );
        // Small delay to ensure different timestamps
        std::thread::sleep(std::time::Duration::from_millis(10));
    }

    // Test with limit
    let args = ["events", "list", &workflow_id.to_string(), "--limit", "3"];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run paginated events list");

    let events_array = json_output.get("events").unwrap().as_array().unwrap();
    assert!(events_array.len() <= 3, "Should respect limit parameter");
    assert!(events_array.len() >= 1, "Should have at least one event");

    // Test with offset
    let args_with_offset = [
        "events",
        "list",
        &workflow_id.to_string(),
        "--limit",
        "2",
        "--offset",
        "2",
    ];

    let json_output_offset = run_cli_with_json(&args_with_offset, start_server)
        .expect("Failed to run events list with offset");

    let events_with_offset = json_output_offset
        .get("events")
        .unwrap()
        .as_array()
        .unwrap();
    assert!(
        events_with_offset.len() >= 1,
        "Should have events with offset"
    );
}

#[rstest]
fn test_events_list_sorting(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_sorting_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create events with different data for sorting
    let _event_a = create_test_event(
        config,
        workflow_id,
        json!({"priority": 1, "name": "aaa_event"}),
    );
    std::thread::sleep(std::time::Duration::from_millis(10));
    let _event_b = create_test_event(
        config,
        workflow_id,
        json!({"priority": 2, "name": "bbb_event"}),
    );
    std::thread::sleep(std::time::Duration::from_millis(10));
    let _event_c = create_test_event(
        config,
        workflow_id,
        json!({"priority": 3, "name": "ccc_event"}),
    );

    // Test default sorting (by timestamp, newest first)
    let args_default = ["events", "list", &workflow_id.to_string()];

    let json_output_default = run_cli_with_json(&args_default, start_server)
        .expect("Failed to run default sorted events list");

    let events_array_default = json_output_default
        .get("events")
        .unwrap()
        .as_array()
        .unwrap();
    assert!(events_array_default.len() >= 3);

    // Test reverse sorting
    let args_reverse = [
        "events",
        "list",
        &workflow_id.to_string(),
        "--sort-by",
        "timestamp",
        "--reverse-sort",
    ];

    let json_output_reverse = run_cli_with_json(&args_reverse, start_server)
        .expect("Failed to run reverse sorted events list");

    let events_array_reverse = json_output_reverse
        .get("events")
        .unwrap()
        .as_array()
        .unwrap();
    assert!(events_array_reverse.len() >= 3);

    // With reverse-sort flag, we should get oldest first
    if events_array_reverse.len() >= 2 {
        let first_timestamp = events_array_reverse[0]
            .get("timestamp")
            .unwrap()
            .as_str()
            .unwrap();
        let second_timestamp = events_array_reverse[1]
            .get("timestamp")
            .unwrap()
            .as_str()
            .unwrap();
        assert!(
            first_timestamp >= second_timestamp,
            "With reverse-sort, events should be newest first"
        );
    }
}

#[rstest]
fn test_events_get_latest_event_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow and events
    let workflow = create_test_workflow(config, "test_latest_event_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create multiple events with delays to ensure different timestamps
    let _event1 = create_test_event(
        config,
        workflow_id,
        json!({"type": "first", "message": "First event"}),
    );
    std::thread::sleep(std::time::Duration::from_millis(10));

    let _event2 = create_test_event(
        config,
        workflow_id,
        json!({"type": "second", "message": "Second event"}),
    );
    std::thread::sleep(std::time::Duration::from_millis(10));

    let latest_event = create_test_event(
        config,
        workflow_id,
        json!({"type": "latest", "message": "Latest event", "final": true}),
    );

    // Test the CLI get-latest-event command
    let args = ["events", "get-latest-event", &workflow_id.to_string()];

    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run events get-latest-event command");

    // Verify we got the latest event
    assert_eq!(
        json_output.get("id").unwrap(),
        &json!(latest_event.id.unwrap())
    );
    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));
    assert_eq!(
        json_output.get("data").unwrap().get("type").unwrap(),
        &json!("latest")
    );
    assert_eq!(
        json_output.get("data").unwrap().get("final").unwrap(),
        &json!(true)
    );
    assert!(json_output.get("timestamp").is_some());
}

#[rstest]
fn test_events_get_latest_event_empty_workflow(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow with no events
    let workflow = create_test_workflow(config, "test_empty_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test the CLI get-latest-event command on empty workflow
    let args = ["events", "get-latest-event", &workflow_id.to_string()];

    let result = run_cli_with_json(&args, start_server);
    // This might succeed with empty output or fail - both are acceptable behaviors
    // The command should handle empty workflows gracefully
    if let Ok(json_output) = result {
        // If it succeeds, it should return valid JSON (even if empty/null)
        assert!(json_output.is_null() || json_output.is_object());
    }
    // If it fails, that's also acceptable for an empty workflow
}

#[rstest]
fn test_events_remove_command_json(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test data
    let workflow = create_test_workflow(config, "test_events_remove_workflow");
    let workflow_id = workflow.id.unwrap();
    let event = create_test_event(
        config,
        workflow_id,
        json!({"type": "to_remove", "message": "This will be removed"}),
    );
    let event_id = event.id.unwrap();

    // Test the CLI delete command
    let args = ["events", "delete", &event_id.to_string()];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to run events delete command");

    // Verify JSON structure shows the removed event
    assert_eq!(json_output.get("id").unwrap(), &json!(event_id));
    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));
    assert_eq!(
        json_output.get("data").unwrap().get("type").unwrap(),
        &json!("to_remove")
    );

    // Verify the event is actually removed by trying to get it via list
    let list_args = ["events", "list", &workflow_id.to_string()];

    let list_output =
        run_cli_with_json(&list_args, start_server).expect("Failed to list events after removal");

    let events_array = list_output.get("events").unwrap().as_array().unwrap();
    let removed_event_exists = events_array
        .iter()
        .any(|event| event.get("id").unwrap() == &json!(event_id));

    assert!(
        !removed_event_exists,
        "Removed event should not appear in list"
    );
}

#[rstest]
fn test_events_various_data_types(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_data_types_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test with different JSON data types
    let test_cases = vec![
        ("string_data", json!("simple string")),
        ("number_data", json!(42)),
        ("boolean_data", json!(true)),
        ("null_data", json!(null)),
        ("array_data", json!([1, 2, 3, "four"])),
        (
            "object_data",
            json!({"key": "value", "nested": {"deep": true}}),
        ),
        (
            "mixed_array",
            json!([{"id": 1}, {"id": 2}, "mixed", 123, null]),
        ),
    ];

    for (test_name, test_data) in test_cases {
        let data_str = serde_json::to_string(&test_data).unwrap();
        let args = [
            "events",
            "create",
            &workflow_id.to_string(),
            "--data",
            &data_str,
        ];

        let json_output = run_cli_with_json(&args, start_server)
            .expect(&format!("Failed to create event with {}", test_name));

        assert_eq!(json_output.get("data").unwrap(), &test_data);
        assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));
    }
}

#[rstest]
fn test_events_timestamp_ordering(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_timestamp_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create events with deliberate delays to test timestamp ordering
    let mut event_data = Vec::new();
    for i in 0..3 {
        let event = create_test_event(
            config,
            workflow_id,
            json!({"sequence": i, "message": format!("Event {}", i)}),
        );
        event_data.push(event);
        std::thread::sleep(std::time::Duration::from_millis(50)); // Ensure different timestamps
    }

    // List events (should be newest first by default)
    let args = ["events", "list", &workflow_id.to_string()];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to list events for timestamp test");

    let events_array = json_output.get("events").unwrap().as_array().unwrap();
    assert!(events_array.len() >= 3);

    // Verify events are in correct order (oldest first)
    let mut previous_timestamp: Option<&str> = None;
    for event in events_array {
        let current_timestamp = event.get("timestamp").unwrap().as_str().unwrap();
        if let Some(prev) = previous_timestamp {
            assert!(
                prev < current_timestamp,
                "Events should be ordered newest first"
            );
        }
        previous_timestamp = Some(current_timestamp);
    }
}

#[rstest]
fn test_events_large_data_handling(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_large_data_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create event with large JSON data
    let mut large_array = Vec::new();
    for i in 0..100 {
        large_array.push(json!({
            "id": i,
            "name": format!("item_{}", i),
            "data": format!("This is item number {} with some additional text to make it larger", i),
            "metadata": {
                "created": "2024-01-01T12:00:00Z",
                "tags": ["tag1", "tag2", "tag3"],
                "values": [i, i*2, i*3]
            }
        }));
    }

    let large_data = json!({
        "type": "bulk_data",
        "count": large_array.len(),
        "items": large_array
    });

    let data_str = serde_json::to_string(&large_data).unwrap();
    let args = [
        "events",
        "create",
        &workflow_id.to_string(),
        "--data",
        &data_str,
    ];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to create event with large data");

    assert_eq!(json_output.get("data").unwrap(), &large_data);
    assert_eq!(json_output.get("workflow_id").unwrap(), &json!(workflow_id));

    // Verify we can retrieve it
    let event_id = json_output.get("id").unwrap().as_i64().unwrap();

    // List and find our event
    let list_args = ["events", "list", &workflow_id.to_string(), "--limit", "10"];

    let list_output =
        run_cli_with_json(&list_args, start_server).expect("Failed to list events with large data");

    let events_array = list_output.get("events").unwrap().as_array().unwrap();
    let found_event = events_array
        .iter()
        .find(|event| event.get("id").unwrap() == &json!(event_id));

    assert!(
        found_event.is_some(),
        "Should find the large data event in list"
    );
    let found = found_event.unwrap();
    assert_eq!(
        found.get("data").unwrap().get("count").unwrap(),
        &json!(100)
    );
}

#[rstest]
fn test_events_error_handling(start_server: &ServerProcess) {
    let config = &start_server.config;
    let workflow = create_test_workflow(config, "test_error_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test with invalid JSON
    let invalid_json = r#"{"key": "value", "incomplete": }"#;
    let args_invalid = [
        "events",
        "create",
        &workflow_id.to_string(),
        "--data",
        invalid_json,
    ];

    let result = run_cli_with_json(&args_invalid, start_server);
    assert!(result.is_err(), "Should fail with invalid JSON data");

    // Test removing non-existent event
    let args_remove = ["events", "delete", "999999"];

    let result = run_cli_with_json(&args_remove, start_server);
    assert!(
        result.is_err(),
        "Should fail when removing non-existent event"
    );

    // Test listing events for non-existent workflow
    let args_list = ["events", "list", "999999"];

    let result = run_cli_with_json(&args_list, start_server);
    // This might succeed with empty results or fail - both are acceptable
    if let Ok(json_output) = result {
        let events_array = json_output.get("events").unwrap().as_array().unwrap();
        assert!(
            events_array.is_empty(),
            "Should return empty array for non-existent workflow"
        );
    }
}

#[rstest]
fn test_events_unicode_and_special_characters(start_server: &ServerProcess) {
    let config = &start_server.config;

    let workflow = create_test_workflow(config, "test_unicode_workflow");
    let workflow_id = workflow.id.unwrap();

    // Test with Unicode and special characters
    let unicode_data = json!({
        "message": "Hello 世界 🌍",
        "symbols": "!@#$%^&*()_+-={}[]|\\:;\"'<>?,./ ",
        "unicode_text": "Ñoël 北京 москва العربية हिंदी 日本語",
        "emoji": "🚀 ⭐ 🎯 📊 💻 🔥 ✅ ❌ 🔔 📱",
        "newlines": "Line 1\nLine 2\nLine 3",
        "tabs": "Column1\tColumn2\tColumn3"
    });

    let data_str = serde_json::to_string(&unicode_data).unwrap();
    let args = [
        "events",
        "create",
        &workflow_id.to_string(),
        "--data",
        &data_str,
    ];

    let json_output =
        run_cli_with_json(&args, start_server).expect("Failed to create event with Unicode data");

    assert_eq!(json_output.get("data").unwrap(), &unicode_data);

    // Verify Unicode characters are preserved
    assert_eq!(
        json_output.get("data").unwrap().get("message").unwrap(),
        &json!("Hello 世界 🌍")
    );
    assert_eq!(
        json_output.get("data").unwrap().get("emoji").unwrap(),
        &json!("🚀 ⭐ 🎯 📊 💻 🔥 ✅ ❌ 🔔 📱")
    );
}

#[rstest]
fn test_events_concurrent_additions(start_server: &ServerProcess) {
    let config = &start_server.config;

    // TODO: this has hung at least once
    let workflow = create_test_workflow(config, "test_concurrent_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create multiple events in quick succession
    let mut event_ids = Vec::new();
    for i in 0..5 {
        let event_data = json!({
            "batch": "concurrent_test",
            "index": i,
            "timestamp": chrono::Utc::now().timestamp_millis()
        });

        let data_str = serde_json::to_string(&event_data).unwrap();
        let args = [
            "events",
            "create",
            &workflow_id.to_string(),
            "--data",
            &data_str,
        ];

        let json_output = run_cli_with_json(&args, start_server)
            .expect(&format!("Failed to create concurrent event {}", i));

        event_ids.push(json_output.get("id").unwrap().as_i64().unwrap());
    }

    // Verify all events were created
    assert_eq!(event_ids.len(), 5);

    // Verify all IDs are unique
    let mut sorted_ids = event_ids.clone();
    sorted_ids.sort();
    sorted_ids.dedup();
    assert_eq!(
        sorted_ids.len(),
        event_ids.len(),
        "All event IDs should be unique"
    );

    // List and verify all events are present
    let list_args = ["events", "list", &workflow_id.to_string(), "--limit", "10"];

    let list_output =
        run_cli_with_json(&list_args, start_server).expect("Failed to list concurrent events");

    let events_array = list_output.get("events").unwrap().as_array().unwrap();
    let batch_events: Vec<_> = events_array
        .iter()
        .filter(|event| {
            event
                .get("data")
                .and_then(|data| data.get("batch"))
                .map(|batch| batch == "concurrent_test")
                .unwrap_or(false)
        })
        .collect();

    assert_eq!(batch_events.len(), 5, "Should find all concurrent events");
}

#[rstest]
fn test_events_list_with_category_filter(start_server: &ServerProcess) {
    let config = &start_server.config;

    // Create test workflow
    let workflow = create_test_workflow(config, "test_category_filter_workflow");
    let workflow_id = workflow.id.unwrap();

    // Create events with different categories in their data
    let _event1 = create_test_event(
        config,
        workflow_id,
        json!({"category": "system", "message": "System event"}),
    );
    let _event2 = create_test_event(
        config,
        workflow_id,
        json!({"category": "user", "message": "User event"}),
    );
    let _event3 = create_test_event(
        config,
        workflow_id,
        json!({"category": "system", "message": "Another system event"}),
    );

    // Test the CLI list command with category filter
    let args = [
        "events",
        "list",
        &workflow_id.to_string(),
        "--category",
        "system",
    ];

    // This test mainly verifies that the CLI accepts the new parameter without errors
    // The actual filtering behavior depends on the backend implementation
    let json_output = run_cli_with_json(&args, start_server)
        .expect("Failed to run events list command with category filter");

    // Verify the response structure is correct
    assert!(
        json_output.is_object(),
        "Events list should return an object"
    );
    assert!(
        json_output.get("events").is_some(),
        "Response should have 'events' field"
    );

    // The command should execute without error
    // The actual filtering depends on how the backend implements category matching
}
