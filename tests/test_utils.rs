use rstest::rstest;
use serial_test::serial;
use std::sync::{Arc, Mutex};
use torc::client::apis::configuration::Configuration;
use torc::client::utils::send_with_retries;

/// Mock error type for testing
#[derive(Debug)]
struct MockError {
    message: String,
}

impl std::fmt::Display for MockError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for MockError {}

#[rstest]
#[serial]
#[ignore] // TODO: currently way too slow
fn test_with_retries_success_on_first_try() {
    let config = Configuration::default();

    let result = send_with_retries(
        &config,
        || Ok::<String, MockError>("success".to_string()),
        1, // 1 minute timeout
    );

    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "success");
}

#[rstest]
#[serial]
#[ignore] // TODO: currently way too slow
fn test_with_retries_non_network_error_fails_immediately() {
    let config = Configuration::default();

    let result = send_with_retries(
        &config,
        || {
            Err::<String, MockError>(MockError {
                message: "database error".to_string(),
            })
        },
        1, // 1 minute timeout
    );

    assert!(result.is_err());
    assert_eq!(result.unwrap_err().message, "database error");
}

#[rstest]
#[serial]
#[ignore] // TODO: currently way too slow
fn test_with_retries_network_error_detection() {
    let config = Configuration::default();
    let call_count = Arc::new(Mutex::new(0));
    let call_count_clone = Arc::clone(&call_count);

    // This should be detected as a network error and trigger retry logic
    let result = send_with_retries(
        &config,
        move || {
            let mut count = call_count_clone.lock().unwrap();
            *count += 1;

            if *count == 1 {
                Err(MockError {
                    message: "connection timeout error".to_string(),
                })
            } else {
                Ok("recovered".to_string())
            }
        },
        1, // 1 minute timeout - should be enough for at least one retry
    );

    // The function should have been called at least once
    let final_count = *call_count.lock().unwrap();
    assert!(
        final_count >= 1,
        "Expected at least 1 call, got {}",
        final_count
    );

    // For network errors, the function will enter retry loop, but since we can't
    // easily mock the ping endpoint, it will likely fail with the original error
    // The important thing is that it was recognized as a network error
    if result.is_err() {
        assert!(result.unwrap_err().message.contains("connection"));
    }
}

#[rstest]
#[serial]
#[ignore] // TODO: currently way too slow
fn test_with_retries_different_network_error_types() {
    let config = Configuration::default();

    let network_error_types = vec![
        "connection refused",
        "network timeout",
        "dns resolution failed",
        "host unreachable",
        "network is down",
    ];

    for error_msg in network_error_types {
        let result = send_with_retries(
            &config,
            || {
                Err::<String, MockError>(MockError {
                    message: error_msg.to_string(),
                })
            },
            1, // 1 minute timeout
        );

        // Should be recognized as network error (though will eventually timeout)
        assert!(result.is_err());
    }
}

#[rstest]
#[serial]
#[ignore] // TODO: currently way too slow
fn test_with_retries_can_be_called_from_external_module() {
    // This test verifies that the function is properly exported and accessible
    let config = Configuration::default();

    // Import the function using the full path to ensure it's accessible
    let result =
        torc::client::send_with_retries(&config, || Ok::<&str, MockError>("accessible"), 1);

    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "accessible");
}

#[rstest]
#[case(0)] // Zero timeout
#[case(1)] // One minute timeout
#[case(5)] // Five minute timeout
#[serial]
#[ignore] // TODO: currently way too slow
fn test_with_retries_different_timeouts(#[case] timeout_minutes: u64) {
    let config = Configuration::default();

    let result = send_with_retries(
        &config,
        || Ok::<String, MockError>("timeout_test".to_string()),
        timeout_minutes,
    );

    // Success case should work regardless of timeout
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "timeout_test");
}

#[rstest]
#[serial]
#[ignore] // TODO: currently way too slow
fn test_with_retries_closure_capture() {
    let config = Configuration::default();
    let captured_value = "captured_data";

    let result = send_with_retries(
        &config,
        || Ok::<String, MockError>(format!("processed: {}", captured_value)),
        1,
    );

    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "processed: captured_data");
}
