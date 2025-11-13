//! Utility functions for pagination.
//!
//! This module provides helper functions that are commonly used across
//! the pagination functionality, such as JSON formatting and display utilities.

use serde_json;

/// Helper function to display results in JSON format with a named field
///
/// This utility function takes any serializable collection of items and
/// formats them as pretty-printed JSON wrapped in an object with a named field.
/// This allows for future extensibility of the API response format.
///
/// # Arguments
/// * `field_name` - The name of the field to use in the JSON object (e.g., "jobs", "files")
/// * `items` - A slice of items that implement `serde::Serialize`
///
/// # Returns
/// `Result<(), serde_json::Error>` - Ok if serialization succeeded, error otherwise
///
/// ```
pub fn display_json_results<T>(field_name: &str, items: &[T]) -> Result<(), serde_json::Error>
where
    T: serde::Serialize,
{
    let output = serde_json::json!({
        field_name: items
    });
    let json = serde_json::to_string_pretty(&output)?;
    println!("{}", json);
    Ok(())
}
