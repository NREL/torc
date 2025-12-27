//! Tests for memory utility functions

use rstest::rstest;
use torc::memory_utils::{memory_string_to_bytes, memory_string_to_gb};

#[rstest]
fn test_memory_string_to_bytes_plain() {
    assert_eq!(memory_string_to_bytes("1024").unwrap(), 1024);
    assert_eq!(memory_string_to_bytes("0").unwrap(), 0);
}

#[rstest]
fn test_memory_string_to_bytes_kibibytes() {
    assert_eq!(memory_string_to_bytes("1k").unwrap(), 1024);
    assert_eq!(memory_string_to_bytes("1K").unwrap(), 1024);
    assert_eq!(memory_string_to_bytes("2k").unwrap(), 2048);
}

#[rstest]
fn test_memory_string_to_bytes_mebibytes() {
    assert_eq!(memory_string_to_bytes("1m").unwrap(), 1024 * 1024);
    assert_eq!(memory_string_to_bytes("1M").unwrap(), 1024 * 1024);
    assert_eq!(memory_string_to_bytes("2M").unwrap(), 2 * 1024 * 1024);
}

#[rstest]
fn test_memory_string_to_bytes_gibibytes() {
    assert_eq!(memory_string_to_bytes("1g").unwrap(), 1024 * 1024 * 1024);
    assert_eq!(memory_string_to_bytes("1G").unwrap(), 1024 * 1024 * 1024);
}

#[rstest]
fn test_memory_string_to_bytes_tebibytes() {
    assert_eq!(
        memory_string_to_bytes("1t").unwrap(),
        1024_i64 * 1024 * 1024 * 1024
    );
    assert_eq!(
        memory_string_to_bytes("1T").unwrap(),
        1024_i64 * 1024 * 1024 * 1024
    );
}

#[rstest]
fn test_memory_string_to_bytes_with_whitespace() {
    assert_eq!(memory_string_to_bytes("  1k  ").unwrap(), 1024);
}

#[rstest]
fn test_memory_string_to_bytes_empty() {
    assert!(memory_string_to_bytes("").is_err());
    assert!(memory_string_to_bytes("   ").is_err());
}

#[rstest]
fn test_memory_string_to_bytes_invalid_unit() {
    assert!(memory_string_to_bytes("1x").is_err());
}

#[rstest]
fn test_memory_string_to_bytes_negative() {
    assert!(memory_string_to_bytes("-1k").is_err());
}

#[rstest]
fn test_memory_string_to_gb() {
    assert!((memory_string_to_gb("1g") - 1.0).abs() < 0.001);
    assert!((memory_string_to_gb("2G") - 2.0).abs() < 0.001);
    assert!((memory_string_to_gb("512M") - 0.5).abs() < 0.001);
}
