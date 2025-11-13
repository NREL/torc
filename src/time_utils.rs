//! Time utility functions

use iso8601;

/// Convert ISO 8601 duration string to seconds
/// Supports formats like "PT1M30S" (1 minute 30 seconds), "P1DT2H" (1 day 2 hours), etc.
pub fn duration_string_to_seconds(duration_str: &str) -> Result<i64, String> {
    let duration_str = duration_str.trim();

    if duration_str.is_empty() {
        return Err("Duration string cannot be empty".to_string());
    }

    // Parse the ISO 8601 duration
    let duration = iso8601::duration(duration_str)
        .map_err(|e| format!("Invalid ISO 8601 duration format: {}", e))?;

    let mut total_seconds = 0_i64;

    // Match on the Duration enum variants
    match duration {
        iso8601::Duration::YMDHMS {
            year,
            month,
            day,
            hour,
            minute,
            second,
            millisecond,
        } => {
            // Convert each component to seconds
            // Approximate: 1 year = 365.25 days = 31,557,600 seconds
            total_seconds = total_seconds
                .checked_add(year as i64 * 31_557_600)
                .ok_or("Duration too large, would cause overflow")?;

            // Approximate: 1 month = 30.44 days = 2,629,800 seconds
            total_seconds = total_seconds
                .checked_add(month as i64 * 2_629_800)
                .ok_or("Duration too large, would cause overflow")?;

            total_seconds = total_seconds
                .checked_add(day as i64 * 86_400)
                .ok_or("Duration too large, would cause overflow")?;

            total_seconds = total_seconds
                .checked_add(hour as i64 * 3_600)
                .ok_or("Duration too large, would cause overflow")?;

            total_seconds = total_seconds
                .checked_add(minute as i64 * 60)
                .ok_or("Duration too large, would cause overflow")?;

            total_seconds = total_seconds
                .checked_add(second as i64)
                .ok_or("Duration too large, would cause overflow")?;

            // Convert milliseconds to seconds (rounded down)
            total_seconds = total_seconds
                .checked_add(millisecond as i64 / 1000)
                .ok_or("Duration too large, would cause overflow")?;
        }
        iso8601::Duration::Weeks(weeks) => {
            // 1 week = 7 days = 604,800 seconds
            total_seconds = total_seconds
                .checked_add(weeks as i64 * 604_800)
                .ok_or("Duration too large, would cause overflow")?;
        }
    }

    Ok(total_seconds)
}
