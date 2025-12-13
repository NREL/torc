use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::client::commands::get_env_user_name;
use crate::client::commands::pagination::utils::display_json_results;
use crate::client::commands::pagination::{EventListParams, paginate_events};
use crate::client::commands::{
    print_error, select_workflow_interactively, table_format::display_table_with_count,
};
use crate::models;
use chrono::{DateTime, Local, Utc};
use serde_json;
use tabled::Tabled;

/// Format a timestamp (milliseconds since epoch) as a human-readable local time string
fn format_timestamp_ms(timestamp_ms: i64) -> String {
    DateTime::from_timestamp_millis(timestamp_ms)
        .map(|dt: DateTime<Utc>| {
            dt.with_timezone(&Local)
                .format("%Y-%m-%d %H:%M:%S%.3f")
                .to_string()
        })
        .unwrap_or_else(|| format!("{}ms", timestamp_ms))
}

#[derive(Tabled)]
struct EventTableRow {
    #[tabled(rename = "ID")]
    id: i64,
    #[tabled(rename = "Timestamp")]
    timestamp: String,
    #[tabled(rename = "Data")]
    data: String,
}

#[derive(clap::Subcommand)]
pub enum EventCommands {
    /// Create a new event
    Create {
        /// Create the event in this workflow.
        #[arg()]
        workflow_id: Option<i64>,
        /// JSON data for the event
        #[arg(short, long)]
        data: String,
    },
    /// List events for a workflow
    List {
        /// List events for this workflow (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Filter events by category
        #[arg(short, long)]
        category: Option<String>,
        /// Maximum number of events to return
        #[arg(short, long, default_value = "10000")]
        limit: i64,
        /// Offset for pagination (0-based)
        #[arg(short, long, default_value = "0")]
        offset: i64,
        /// Field to sort by
        #[arg(short, long)]
        sort_by: Option<String>,
        /// Reverse sort order
        #[arg(short, long, default_value = "false")]
        reverse_sort: bool,
    },
    /// Monitor events for a workflow in real-time
    Monitor {
        /// Monitor events for this workflow (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
        /// Duration to monitor in minutes (default: infinite)
        #[arg(short, long)]
        duration: Option<i64>,
        /// Poll interval in seconds (default: 60)
        #[arg(short, long, default_value = "60")]
        poll_interval: i64,
        /// Filter events by category
        #[arg(short, long)]
        category: Option<String>,
    },
    /// Get the latest event for a workflow
    GetLatestEvent {
        /// Get the latest event for this workflow (optional - will prompt if not provided)
        #[arg()]
        workflow_id: Option<i64>,
    },
    /// Delete an event
    Delete {
        /// ID of the event to remove
        id: i64,
    },
}

pub fn handle_event_commands(config: &Configuration, command: &EventCommands, format: &str) {
    match command {
        EventCommands::Create { workflow_id, data } => {
            let user_name = crate::client::commands::get_env_user_name();
            let wf_id = workflow_id.unwrap_or_else(|| {
                select_workflow_interactively(config, &user_name).unwrap_or_else(|e| {
                    eprintln!("Error selecting workflow: {}", e);
                    std::process::exit(1);
                })
            });

            let json_data: serde_json::Value = match serde_json::from_str(data) {
                Ok(json) => json,
                Err(e) => {
                    eprintln!("Error parsing JSON data: {}", e);
                    std::process::exit(1);
                }
            };

            let event = models::EventModel::new(wf_id, json_data);

            match default_api::create_event(config, event) {
                Ok(created_event) => {
                    if format == "json" {
                        match serde_json::to_string_pretty(&created_event) {
                            Ok(json) => println!("{}", json),
                            Err(e) => {
                                eprintln!("Error serializing event to JSON: {}", e);
                                std::process::exit(1);
                            }
                        }
                    } else {
                        println!("Successfully created event:");
                        println!("  ID: {}", created_event.id.unwrap_or(-1));
                        println!("  Workflow ID: {}", created_event.workflow_id);
                        println!(
                            "  Timestamp: {}",
                            format_timestamp_ms(created_event.timestamp)
                        );
                        println!(
                            "  Data: {}",
                            serde_json::to_string_pretty(&created_event.data)
                                .unwrap_or_else(|_| "Unable to display data".to_string())
                        );
                    }
                }
                Err(e) => {
                    print_error("creating event", &e);
                    std::process::exit(1);
                }
            }
        }
        EventCommands::List {
            workflow_id,
            category,
            limit,
            offset,
            sort_by,
            reverse_sort,
        } => {
            let user_name = get_env_user_name();
            let selected_workflow_id = match workflow_id {
                Some(id) => *id,
                None => select_workflow_interactively(config, &user_name).unwrap(),
            };

            let mut params = EventListParams::new()
                .with_offset(*offset)
                .with_limit(*limit);

            if let Some(category_str) = category {
                params = params.with_category(category_str.clone());
            }

            if let Some(sort_by_str) = sort_by {
                params = params.with_sort_by(sort_by_str.clone());
            }

            params = params.with_reverse_sort(*reverse_sort);

            match paginate_events(config, selected_workflow_id as i64, params) {
                Ok(events) => {
                    if format == "json" {
                        match display_json_results("events", &events) {
                            Ok(()) => {}
                            Err(e) => {
                                eprintln!("Error serializing events to JSON: {}", e);
                                std::process::exit(1);
                            }
                        }
                    } else {
                        if events.is_empty() {
                            println!("No events found for workflow {}", selected_workflow_id);
                        } else {
                            println!("Events for workflow {}:", selected_workflow_id);
                            let rows: Vec<EventTableRow> = events
                                .iter()
                                .map(|event| EventTableRow {
                                    id: event.id.unwrap_or(-1),
                                    timestamp: format_timestamp_ms(event.timestamp),
                                    data: serde_json::to_string(&event.data)
                                        .unwrap_or_else(|_| "Unable to display".to_string()),
                                })
                                .collect();
                            display_table_with_count(&rows, "events");
                        }
                    }
                }
                Err(e) => {
                    print_error("listing events", &e);
                    std::process::exit(1);
                }
            }
        }
        EventCommands::Monitor {
            workflow_id,
            duration,
            poll_interval,
            category,
        } => {
            let user_name = get_env_user_name();
            let selected_workflow_id = match workflow_id {
                Some(id) => *id,
                None => select_workflow_interactively(config, &user_name).unwrap(),
            };

            handle_monitor_events(
                config,
                selected_workflow_id,
                *duration,
                *poll_interval,
                category,
                format,
            );
        }
        EventCommands::GetLatestEvent { workflow_id } => {
            let user_name = get_env_user_name();
            let selected_workflow_id = match workflow_id {
                Some(id) => *id,
                None => select_workflow_interactively(config, &user_name).unwrap(),
            };

            match default_api::list_events(
                config,
                selected_workflow_id as i64,
                None,              // offset
                Some(1),           // limit to 1 event
                Some("timestamp"), // sort by timestamp
                Some(true),        // reverse sort (newest first)
                None,              // category
                None,              // after_timestamp
            ) {
                Ok(response) => {
                    if let Some(events) = response.items {
                        if let Some(latest_event) = events.first() {
                            if format == "json" {
                                match serde_json::to_string_pretty(&latest_event) {
                                    Ok(json) => println!("{}", json),
                                    Err(e) => {
                                        eprintln!("Error serializing event to JSON: {}", e);
                                        std::process::exit(1);
                                    }
                                }
                            } else {
                                println!("Latest event for workflow {}:", selected_workflow_id);
                                println!("  ID: {}", latest_event.id.unwrap_or(-1));
                                println!(
                                    "  Timestamp: {}",
                                    format_timestamp_ms(latest_event.timestamp)
                                );
                                println!(
                                    "  Data: {}",
                                    serde_json::to_string_pretty(&latest_event.data)
                                        .unwrap_or_else(|_| "Unable to display data".to_string())
                                );
                            }
                        } else {
                            println!("No events found for workflow {}", selected_workflow_id);
                        }
                    } else {
                        println!("No events found for workflow {}", selected_workflow_id);
                    }
                }
                Err(e) => {
                    print_error("getting latest event", &e);
                    std::process::exit(1);
                }
            }
        }
        EventCommands::Delete { id } => match default_api::delete_event(config, *id, None) {
            Ok(removed_event) => {
                if format == "json" {
                    match serde_json::to_string_pretty(&removed_event) {
                        Ok(json) => println!("{}", json),
                        Err(e) => {
                            eprintln!("Error serializing event to JSON: {}", e);
                            std::process::exit(1);
                        }
                    }
                } else {
                    println!("Successfully removed event:");
                    println!("  ID: {}", removed_event.id.unwrap_or(-1));
                    println!("  Workflow ID: {}", removed_event.workflow_id);
                }
            }
            Err(e) => {
                print_error("removing event", &e);
                std::process::exit(1);
            }
        },
    }
}

fn handle_monitor_events(
    config: &Configuration,
    workflow_id: i64,
    duration: Option<i64>,
    poll_interval: i64,
    category: &Option<String>,
    format: &str,
) {
    use std::thread;
    use std::time::{Duration as StdDuration, Instant};

    // Get the latest event timestamp to start monitoring from (in milliseconds since epoch)
    // Use list_events with limit=1 and reverse_sort=true to get the newest event
    let mut last_timestamp_ms: i64 = match default_api::list_events(
        config,
        workflow_id,
        None,       // offset
        Some(1),    // limit to 1 event
        Some("id"), // sort by id
        Some(true), // reverse sort (newest first)
        None,       // category
        None,       // after_timestamp
    ) {
        Ok(response) => {
            // Extract the timestamp from the latest event
            response
                .items
                .and_then(|items| items.first().map(|e| e.timestamp))
                .unwrap_or(0)
        }
        Err(e) => {
            // If there are no events yet, start from 0
            eprintln!(
                "Note: No events found yet, starting from epoch. Error: {:?}",
                e
            );
            0
        }
    };

    let start_time = Instant::now();
    let duration_seconds = duration.map(|d| d * 60); // Convert minutes to seconds

    eprintln!(
        "Monitoring events for workflow {} (poll interval: {}s{})",
        workflow_id,
        poll_interval,
        match duration {
            Some(d) => format!(", duration: {} minutes", d),
            None => String::from(", duration: infinite"),
        }
    );

    if let Some(cat) = category {
        println!("Filtering by category: {}", cat);
    }

    eprintln!(
        "Starting from timestamp: {}",
        format_timestamp_ms(last_timestamp_ms)
    );
    eprintln!("Press Ctrl+C to stop monitoring\n");

    loop {
        // Check if we've exceeded the duration
        if let Some(max_seconds) = duration_seconds {
            if start_time.elapsed().as_secs() >= max_seconds as u64 {
                println!("\nMonitoring duration completed.");
                break;
            }
        }

        // Fetch events after the last timestamp (timestamp is in milliseconds)
        match default_api::list_events(
            config,
            workflow_id,
            None, // offset
            None, // limit (get all new events)
            None, // sort_by
            None, // reverse_sort
            category.as_deref(),
            Some(last_timestamp_ms),
        ) {
            Ok(response) => {
                if let Some(events) = response.items {
                    if !events.is_empty() {
                        // Process new events
                        for event in &events {
                            if format == "json" {
                                match serde_json::to_string(&event) {
                                    Ok(json) => println!("{}", json),
                                    Err(e) => {
                                        eprintln!("Error serializing event to JSON: {}", e);
                                    }
                                }
                            } else {
                                println!(
                                    "[{}] Event ID {}: {}",
                                    format_timestamp_ms(event.timestamp),
                                    event.id.unwrap_or(-1),
                                    serde_json::to_string(&event.data)
                                        .unwrap_or_else(|_| "Unable to display".to_string())
                                );
                            }
                        }

                        // Update last_timestamp_ms to the newest event's timestamp
                        // Timestamp is now stored as i64 milliseconds, no parsing needed
                        if let Some(latest_event) = events.last() {
                            last_timestamp_ms = latest_event.timestamp;
                        }
                    }
                }
            }
            Err(e) => {
                eprintln!("Error fetching events: {:?}", e);
            }
        }

        // Sleep for poll_interval seconds
        thread::sleep(StdDuration::from_secs(poll_interval as u64));
    }
}
