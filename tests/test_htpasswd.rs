//! Tests for the torc-htpasswd utility

use std::process::Command;

fn get_exe_path(path: &str) -> String {
    std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join(path)
        .to_string_lossy()
        .to_string()
}

/// Test that the hash command outputs a valid htpasswd line to stdout
#[test]
fn test_hash_command_with_explicit_username() {
    let output = Command::new(get_exe_path("./target/debug/torc-htpasswd"))
        .arg("hash")
        .arg("--password")
        .arg("testpassword123")
        .arg("testuser")
        .output()
        .expect("Failed to run torc-htpasswd hash");

    assert!(output.status.success(), "hash command should succeed");

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    // stdout should contain the htpasswd line
    assert!(
        stdout.starts_with("testuser:$2b$12$"),
        "stdout should contain htpasswd line starting with 'testuser:$2b$12$', got: {}",
        stdout
    );

    // stderr should contain progress messages
    assert!(
        stderr.contains("Hashing password"),
        "stderr should contain progress message, got: {}",
        stderr
    );
    assert!(
        stderr.contains("Send the line above"),
        "stderr should contain instruction message, got: {}",
        stderr
    );
}

/// Test that the hash command defaults to $USER when no username is provided
#[test]
fn test_hash_command_defaults_to_env_user() {
    let output = Command::new(get_exe_path("./target/debug/torc-htpasswd"))
        .arg("hash")
        .arg("--password")
        .arg("testpassword123")
        .env("USER", "envuser")
        .output()
        .expect("Failed to run torc-htpasswd hash");

    assert!(output.status.success(), "hash command should succeed");

    let stdout = String::from_utf8_lossy(&output.stdout);

    // stdout should contain the htpasswd line with the username from $USER
    assert!(
        stdout.starts_with("envuser:$2b$12$"),
        "stdout should contain htpasswd line starting with 'envuser:$2b$12$', got: {}",
        stdout
    );
}

/// Test that the hash command falls back to $USERNAME when $USER is not set
#[test]
fn test_hash_command_falls_back_to_username_env() {
    let output = Command::new(get_exe_path("./target/debug/torc-htpasswd"))
        .arg("hash")
        .arg("--password")
        .arg("testpassword123")
        .env_remove("USER")
        .env("USERNAME", "winuser")
        .output()
        .expect("Failed to run torc-htpasswd hash");

    assert!(output.status.success(), "hash command should succeed");

    let stdout = String::from_utf8_lossy(&output.stdout);

    // stdout should contain the htpasswd line with the username from $USERNAME
    assert!(
        stdout.starts_with("winuser:$2b$12$"),
        "stdout should contain htpasswd line starting with 'winuser:$2b$12$', got: {}",
        stdout
    );
}

/// Test that the hash command fails when no username is provided and env vars are not set
#[test]
fn test_hash_command_fails_without_username_or_env() {
    let output = Command::new(get_exe_path("./target/debug/torc-htpasswd"))
        .arg("hash")
        .arg("--password")
        .arg("testpassword123")
        .env_remove("USER")
        .env_remove("USERNAME")
        .output()
        .expect("Failed to run torc-htpasswd hash");

    assert!(
        !output.status.success(),
        "hash command should fail when no username available"
    );

    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        stderr.contains("could not read from $USER or $USERNAME"),
        "stderr should contain error about missing username, got: {}",
        stderr
    );
}

/// Test that explicit username overrides environment variable
#[test]
fn test_hash_command_explicit_username_overrides_env() {
    let output = Command::new(get_exe_path("./target/debug/torc-htpasswd"))
        .arg("hash")
        .arg("--password")
        .arg("testpassword123")
        .arg("explicituser")
        .env("USER", "envuser")
        .output()
        .expect("Failed to run torc-htpasswd hash");

    assert!(output.status.success(), "hash command should succeed");

    let stdout = String::from_utf8_lossy(&output.stdout);

    // Explicit username should be used, not the env var
    assert!(
        stdout.starts_with("explicituser:$2b$12$"),
        "stdout should use explicit username 'explicituser', not env var, got: {}",
        stdout
    );
}

/// Test that custom cost factor is used
#[test]
fn test_hash_command_custom_cost() {
    let output = Command::new(get_exe_path("./target/debug/torc-htpasswd"))
        .arg("hash")
        .arg("--password")
        .arg("testpassword123")
        .arg("--cost")
        .arg("4")
        .arg("testuser")
        .output()
        .expect("Failed to run torc-htpasswd hash");

    assert!(output.status.success(), "hash command should succeed");

    let stdout = String::from_utf8_lossy(&output.stdout);

    // With cost 4, the hash should start with $2b$04$
    assert!(
        stdout.starts_with("testuser:$2b$04$"),
        "stdout should contain hash with cost 4 ($2b$04$), got: {}",
        stdout
    );
}
