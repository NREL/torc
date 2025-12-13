use chrono::{DateTime, Local, Utc};
use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Cell, Row, Table, Tabs},
};

use super::app::{App, DetailViewType, Focus, PopupType};
use super::components::HelpPopup;

/// Format a timestamp (milliseconds since epoch) as a human-readable local time string
fn format_timestamp_ms(timestamp_ms: i64) -> String {
    DateTime::from_timestamp_millis(timestamp_ms)
        .map(|dt: DateTime<Utc>| {
            dt.with_timezone(&Local)
                .format("%Y-%m-%d %H:%M:%S")
                .to_string()
        })
        .unwrap_or_else(|| format!("{}ms", timestamp_ms))
}

/// Format bytes into human-readable format (KB, MB, GB)
fn format_bytes(bytes: i64) -> String {
    const KB: f64 = 1024.0;
    const MB: f64 = KB * 1024.0;
    const GB: f64 = MB * 1024.0;

    let bytes_f = bytes as f64;
    if bytes_f >= GB {
        format!("{:.1} GB", bytes_f / GB)
    } else if bytes_f >= MB {
        format!("{:.1} MB", bytes_f / MB)
    } else if bytes_f >= KB {
        format!("{:.1} KB", bytes_f / KB)
    } else {
        format!("{} B", bytes)
    }
}

pub fn draw(f: &mut Frame, app: &mut App) {
    let main_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),      // Help text
            Constraint::Length(3),      // Server URL + status display
            Constraint::Length(3),      // User filter display
            Constraint::Percentage(40), // Workflows table
            Constraint::Length(3),      // Tabs
            Constraint::Min(10),        // Detail table + filter/url/user input
        ])
        .split(f.area());

    draw_help(f, main_chunks[0], app);
    draw_server_url(f, main_chunks[1], app);
    draw_user_filter(f, main_chunks[2], app);
    draw_workflows_table(f, main_chunks[3], app);
    draw_tabs(f, main_chunks[4], app);

    // Split the bottom section for detail table and input widgets
    let needs_input = app.focus == Focus::FilterInput
        || app.focus == Focus::ServerUrlInput
        || app.focus == Focus::UserInput
        || app.focus == Focus::WorkflowPathInput;

    let detail_chunks = if needs_input {
        Layout::default()
            .direction(Direction::Vertical)
            .constraints([Constraint::Min(5), Constraint::Length(3)])
            .split(main_chunks[5])
    } else {
        Layout::default()
            .direction(Direction::Vertical)
            .constraints([Constraint::Min(5)])
            .split(main_chunks[5])
    };

    draw_detail_table(f, detail_chunks[0], app);

    if app.focus == Focus::FilterInput {
        draw_filter_input(f, detail_chunks[1], app);
    } else if app.focus == Focus::ServerUrlInput {
        draw_server_url_input(f, detail_chunks[1], app);
    } else if app.focus == Focus::UserInput {
        draw_user_input(f, detail_chunks[1], app);
    } else if app.focus == Focus::WorkflowPathInput {
        draw_workflow_path_input(f, detail_chunks[1], app);
    }

    // Draw popups on top of everything
    if let Some(ref popup) = app.popup {
        match popup {
            PopupType::Help => {
                HelpPopup::render(f, f.area(), "");
            }
            PopupType::Confirmation { dialog, .. } => {
                dialog.render(f, f.area());
            }
            PopupType::JobDetails(details) => {
                details.render(f, f.area());
            }
            PopupType::LogViewer(viewer) => {
                viewer.render(f, f.area());
            }
            PopupType::FileViewer(viewer) => {
                viewer.render(f, f.area());
            }
            PopupType::ProcessViewer(viewer) => {
                viewer.render(f, f.area());
            }
            PopupType::Error(dialog) => {
                dialog.render(f, f.area());
            }
        }
    }
}

fn draw_help(f: &mut Frame, area: Rect, app: &App) {
    let help_text = if app.focus == Focus::FilterInput {
        vec![Line::from(vec![
            Span::styled("Type", Style::default().fg(Color::Yellow)),
            Span::raw(": enter filter | "),
            Span::styled("Tab", Style::default().fg(Color::Yellow)),
            Span::raw(": change column | "),
            Span::styled("Enter", Style::default().fg(Color::Yellow)),
            Span::raw(": apply | "),
            Span::styled("Esc", Style::default().fg(Color::Yellow)),
            Span::raw(": cancel"),
        ])]
    } else if app.focus == Focus::ServerUrlInput {
        vec![Line::from(vec![
            Span::styled("Type", Style::default().fg(Color::Yellow)),
            Span::raw(": enter URL | "),
            Span::styled("Enter", Style::default().fg(Color::Yellow)),
            Span::raw(": connect | "),
            Span::styled("Esc", Style::default().fg(Color::Yellow)),
            Span::raw(": cancel"),
        ])]
    } else if app.focus == Focus::UserInput {
        vec![Line::from(vec![
            Span::styled("Type", Style::default().fg(Color::Yellow)),
            Span::raw(": enter username | "),
            Span::styled("Enter", Style::default().fg(Color::Yellow)),
            Span::raw(": apply | "),
            Span::styled("Esc", Style::default().fg(Color::Yellow)),
            Span::raw(": cancel"),
        ])]
    } else if app.focus == Focus::WorkflowPathInput {
        vec![Line::from(vec![
            Span::styled("Type", Style::default().fg(Color::Yellow)),
            Span::raw(": enter path to workflow spec file | "),
            Span::styled("Enter", Style::default().fg(Color::Yellow)),
            Span::raw(": create | "),
            Span::styled("Esc", Style::default().fg(Color::Yellow)),
            Span::raw(": cancel"),
        ])]
    } else if app.focus == Focus::Details && app.detail_view == DetailViewType::Jobs {
        // Job-specific help when in Jobs tab
        vec![Line::from(vec![
            Span::styled("?", Style::default().fg(Color::Yellow)),
            Span::raw(": help | "),
            Span::styled("Enter", Style::default().fg(Color::Yellow)),
            Span::raw(": details | "),
            Span::styled("l", Style::default().fg(Color::Yellow)),
            Span::raw(": logs | "),
            Span::styled("c", Style::default().fg(Color::Yellow)),
            Span::raw(": cancel | "),
            Span::styled("t", Style::default().fg(Color::Yellow)),
            Span::raw(": terminate | "),
            Span::styled("y", Style::default().fg(Color::Yellow)),
            Span::raw(": retry | "),
            Span::styled("f", Style::default().fg(Color::Yellow)),
            Span::raw(": filter | "),
            Span::styled("Tab", Style::default().fg(Color::Yellow)),
            Span::raw(": next tab"),
        ])]
    } else if app.focus == Focus::Details && app.detail_view == DetailViewType::Files {
        // File-specific help when in Files tab
        vec![Line::from(vec![
            Span::styled("?", Style::default().fg(Color::Yellow)),
            Span::raw(": help | "),
            Span::styled("Enter", Style::default().fg(Color::Yellow)),
            Span::raw(": view file | "),
            Span::styled("f", Style::default().fg(Color::Yellow)),
            Span::raw(": filter | "),
            Span::styled("c", Style::default().fg(Color::Yellow)),
            Span::raw(": clear filter | "),
            Span::styled("Tab", Style::default().fg(Color::Yellow)),
            Span::raw(": next tab"),
        ])]
    } else {
        // General help
        vec![Line::from(vec![
            Span::styled("?", Style::default().fg(Color::Yellow)),
            Span::raw(": help | "),
            Span::styled("n", Style::default().fg(Color::Yellow)),
            Span::raw(": new | "),
            Span::styled("i", Style::default().fg(Color::Yellow)),
            Span::raw(": init | "),
            Span::styled("I", Style::default().fg(Color::Yellow)),
            Span::raw(": reinit | "),
            Span::styled("R", Style::default().fg(Color::Yellow)),
            Span::raw(": reset | "),
            Span::styled("x", Style::default().fg(Color::Yellow)),
            Span::raw(": run | "),
            Span::styled("s", Style::default().fg(Color::Yellow)),
            Span::raw(": submit | "),
            Span::styled("d", Style::default().fg(Color::Yellow)),
            Span::raw(": delete | "),
            Span::styled("r", Style::default().fg(Color::Yellow)),
            Span::raw(": refresh"),
        ])]
    };

    // Build title with status message if present
    let title = if let Some(ref status) = app.status_message {
        if status.is_visible() {
            format!("Torc Management Console - {}", status.message)
        } else {
            "Torc Management Console".to_string()
        }
    } else {
        "Torc Management Console".to_string()
    };

    let title_style = if let Some(ref status) = app.status_message {
        if status.is_visible() {
            Style::default().fg(status.color())
        } else {
            Style::default()
        }
    } else {
        Style::default()
    };

    let block = Block::default()
        .borders(Borders::ALL)
        .title(Span::styled(title, title_style));

    let paragraph = ratatui::widgets::Paragraph::new(help_text)
        .block(block)
        .style(Style::default().fg(Color::White));

    f.render_widget(paragraph, area);
}

fn draw_server_url(f: &mut Frame, area: Rect, app: &App) {
    // Server status indicator
    let (status_icon, status_color) = if app.is_server_running() {
        ("● ", Color::Green) // Running
    } else if app.server_process.is_some() {
        ("○ ", Color::Yellow) // Stopped but was started
    } else {
        ("", Color::White) // Not managed
    };

    let mut spans = vec![
        Span::styled("Server: ", Style::default().fg(Color::White)),
        Span::styled(status_icon, Style::default().fg(status_color)),
        Span::styled(&app.server_url, Style::default().fg(Color::Cyan)),
        Span::styled(" | ", Style::default().fg(Color::DarkGray)),
        Span::styled("u", Style::default().fg(Color::Yellow)),
        Span::styled(": URL ", Style::default().fg(Color::DarkGray)),
    ];

    // Add server management hints
    if app.is_server_running() {
        spans.extend(vec![
            Span::styled("K", Style::default().fg(Color::Yellow)),
            Span::styled(": stop ", Style::default().fg(Color::DarkGray)),
            Span::styled("O", Style::default().fg(Color::Yellow)),
            Span::styled(": output", Style::default().fg(Color::DarkGray)),
        ]);
    } else {
        spans.extend(vec![
            Span::styled("S", Style::default().fg(Color::Yellow)),
            Span::styled(": start server", Style::default().fg(Color::DarkGray)),
        ]);
    }

    let text = vec![Line::from(spans)];

    let block = Block::default().borders(Borders::ALL).title("Connection");

    let paragraph = ratatui::widgets::Paragraph::new(text)
        .block(block)
        .style(Style::default().fg(Color::White));

    f.render_widget(paragraph, area);
}

fn draw_user_filter(f: &mut Frame, area: Rect, app: &App) {
    let user_display = app.get_current_user_display();
    let text = vec![Line::from(vec![
        Span::styled("User: ", Style::default().fg(Color::White)),
        Span::styled(&user_display, Style::default().fg(Color::Cyan)),
        Span::styled(" | Press ", Style::default().fg(Color::DarkGray)),
        Span::styled("w", Style::default().fg(Color::Yellow)),
        Span::styled(" to change, ", Style::default().fg(Color::DarkGray)),
        Span::styled("a", Style::default().fg(Color::Yellow)),
        Span::styled(" to toggle all users", Style::default().fg(Color::DarkGray)),
    ])];

    let block = Block::default().borders(Borders::ALL).title("User Filter");

    let paragraph = ratatui::widgets::Paragraph::new(text)
        .block(block)
        .style(Style::default().fg(Color::White));

    f.render_widget(paragraph, area);
}

fn draw_workflows_table(f: &mut Frame, area: Rect, app: &mut App) {
    let selected_style = Style::default()
        .add_modifier(Modifier::REVERSED)
        .fg(Color::Cyan);
    let header_style = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);

    let header = Row::new(vec!["ID", "Name", "User", "Description"])
        .style(header_style)
        .bottom_margin(1);

    let rows = app.workflows.iter().map(|workflow| {
        let id = workflow.id.map(|i| i.to_string()).unwrap_or_default();
        let name = workflow.name.clone();
        let user = workflow.user.clone();
        let description = workflow
            .description
            .clone()
            .unwrap_or_else(|| String::from(""));

        Row::new(vec![
            Cell::from(id),
            Cell::from(name),
            Cell::from(user),
            Cell::from(description),
        ])
    });

    let title = if app.focus == Focus::Workflows {
        "Workflows [FOCUSED] (Press Enter to load details)"
    } else {
        "Workflows (Press Enter to load details)"
    };

    let border_style = if app.focus == Focus::Workflows {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(8),
            Constraint::Length(20),
            Constraint::Length(15),
            Constraint::Percentage(100),
        ],
    )
    .header(header)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style),
    )
    .row_highlight_style(selected_style)
    .highlight_symbol(">> ");

    f.render_stateful_widget(table, area, &mut app.workflows_state);
}

fn draw_tabs(f: &mut Frame, area: Rect, app: &App) {
    let all_types = DetailViewType::all();
    let titles: Vec<&str> = all_types.iter().map(|t| t.as_str()).collect();

    let selected = match app.detail_view {
        DetailViewType::Jobs => 0,
        DetailViewType::Files => 1,
        DetailViewType::Events => 2,
        DetailViewType::Results => 3,
        DetailViewType::ScheduledNodes => 4,
        DetailViewType::Dag => 5,
    };

    let tabs = Tabs::new(titles)
        .block(Block::default().borders(Borders::ALL).title("Detail View"))
        .select(selected)
        .style(Style::default().fg(Color::White))
        .highlight_style(
            Style::default()
                .fg(Color::Yellow)
                .add_modifier(Modifier::BOLD),
        );

    f.render_widget(tabs, area);
}

fn draw_detail_table(f: &mut Frame, area: Rect, app: &mut App) {
    match app.detail_view {
        DetailViewType::Jobs => draw_jobs_table(f, area, app),
        DetailViewType::Files => draw_files_table(f, area, app),
        DetailViewType::Events => draw_events_table(f, area, app),
        DetailViewType::Results => draw_results_table(f, area, app),
        DetailViewType::ScheduledNodes => draw_scheduled_nodes_table(f, area, app),
        DetailViewType::Dag => draw_dag(f, area, app),
    }
}

fn draw_jobs_table(f: &mut Frame, area: Rect, app: &mut App) {
    let selected_style = Style::default()
        .add_modifier(Modifier::REVERSED)
        .fg(Color::Cyan);
    let header_style = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);

    let header = Row::new(vec!["ID", "Name", "Status", "Command"])
        .style(header_style)
        .bottom_margin(1);

    let rows = app.jobs.iter().map(|job| {
        let id = job.id.map(|i| i.to_string()).unwrap_or_default();
        let name = job.name.clone();
        let status_str = job
            .status
            .as_ref()
            .map(|s| format!("{:?}", s))
            .unwrap_or_default();

        // Color the status based on its value
        let status_color = match status_str.as_str() {
            "Completed" => Color::Green,
            "Running" => Color::Yellow,
            "Failed" => Color::Red,
            "Canceled" | "Terminated" => Color::Magenta,
            "Ready" => Color::Cyan,
            "Blocked" => Color::DarkGray,
            "Pending" | "Scheduled" => Color::Blue,
            _ => Color::White,
        };

        let command = job.command.clone();

        Row::new(vec![
            Cell::from(id),
            Cell::from(name),
            Cell::from(Span::styled(status_str, Style::default().fg(status_color))),
            Cell::from(command),
        ])
    });

    let title = if app.focus == Focus::Details {
        "Jobs [FOCUSED] - Enter: details, l: logs, c: cancel, t: terminate, y: retry"
    } else {
        "Jobs"
    };

    let border_style = if app.focus == Focus::Details {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(8),
            Constraint::Length(20),
            Constraint::Length(15),
            Constraint::Percentage(100),
        ],
    )
    .header(header)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style),
    )
    .row_highlight_style(selected_style)
    .highlight_symbol(">> ");

    f.render_stateful_widget(table, area, &mut app.jobs_state);
}

/// Format epoch seconds as ISO 8601 timestamp
fn format_timestamp(epoch_secs: f64) -> String {
    use chrono::{DateTime, Utc};
    let secs = epoch_secs as i64;
    let nsecs = ((epoch_secs - secs as f64) * 1_000_000_000.0) as u32;
    DateTime::<Utc>::from_timestamp(secs, nsecs)
        .map(|dt| dt.format("%Y-%m-%dT%H:%M:%SZ").to_string())
        .unwrap_or_default()
}

fn draw_files_table(f: &mut Frame, area: Rect, app: &mut App) {
    let is_focused = app.focus == Focus::Details;
    let selected_style = Style::default()
        .add_modifier(Modifier::REVERSED)
        .fg(Color::Cyan);
    let header_style = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);

    let header = Row::new(vec!["ID", "Name", "Path", "Modified"])
        .style(header_style)
        .bottom_margin(1);

    let rows = app.files.iter().map(|file| {
        let id = file.id.map(|i| i.to_string()).unwrap_or_default();
        let name = file.name.clone();
        let path = file.path.clone();
        let st_mtime = file
            .st_mtime
            .map(|t| format_timestamp(t))
            .unwrap_or_default();

        Row::new(vec![
            Cell::from(id),
            Cell::from(name),
            Cell::from(path),
            Cell::from(st_mtime),
        ])
    });

    let title = if is_focused {
        "Files [FOCUSED]"
    } else {
        "Files"
    };
    let border_style = if is_focused {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(8),
            Constraint::Length(20),
            Constraint::Percentage(50),
            Constraint::Length(20),
        ],
    )
    .header(header)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style),
    )
    .row_highlight_style(selected_style)
    .highlight_symbol(">> ");

    f.render_stateful_widget(table, area, &mut app.files_state);
}

fn draw_events_table(f: &mut Frame, area: Rect, app: &mut App) {
    let is_focused = app.focus == Focus::Details;
    let selected_style = Style::default()
        .add_modifier(Modifier::REVERSED)
        .fg(Color::Cyan);
    let header_style = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);

    let header = Row::new(vec!["ID", "Workflow ID", "Data", "Timestamp"])
        .style(header_style)
        .bottom_margin(1);

    let rows = app.events.iter().map(|event| {
        let id = event.id.map(|i| i.to_string()).unwrap_or_default();
        let workflow_id = event.workflow_id.to_string();
        let data = event.data.to_string();
        let timestamp = format_timestamp_ms(event.timestamp);

        Row::new(vec![
            Cell::from(id),
            Cell::from(workflow_id),
            Cell::from(data),
            Cell::from(timestamp),
        ])
    });

    let title = if is_focused {
        "Events [FOCUSED]"
    } else {
        "Events"
    };
    let border_style = if is_focused {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(8),
            Constraint::Length(12),
            Constraint::Percentage(60),
            Constraint::Length(20),
        ],
    )
    .header(header)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style),
    )
    .row_highlight_style(selected_style)
    .highlight_symbol(">> ");

    f.render_stateful_widget(table, area, &mut app.events_state);
}

fn draw_results_table(f: &mut Frame, area: Rect, app: &mut App) {
    let is_focused = app.focus == Focus::Details;
    let selected_style = Style::default()
        .add_modifier(Modifier::REVERSED)
        .fg(Color::Cyan);
    let header_style = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);

    let header = Row::new(vec![
        "ID", "Job ID", "Run", "Return", "Status", "Peak Mem", "Peak CPU",
    ])
    .style(header_style)
    .bottom_margin(1);

    let rows = app.results.iter().map(|result| {
        let id = result.id.map(|i| i.to_string()).unwrap_or_default();
        let job_id = result.job_id.to_string();
        let run_id = result.run_id.to_string();
        let return_code = result.return_code;
        let status = format!("{:?}", result.status);

        // Format peak memory (bytes to human readable)
        let peak_mem = result
            .peak_memory_bytes
            .map(|bytes| format_bytes(bytes))
            .unwrap_or_else(|| "-".to_string());

        // Format peak CPU percentage
        let peak_cpu = result
            .peak_cpu_percent
            .map(|pct| format!("{:.1}%", pct))
            .unwrap_or_else(|| "-".to_string());

        // Color based on return code
        let row_color = if return_code == 0 {
            Color::Green
        } else {
            Color::Red
        };

        Row::new(vec![
            Cell::from(id),
            Cell::from(job_id),
            Cell::from(run_id),
            Cell::from(Span::styled(
                return_code.to_string(),
                Style::default().fg(row_color),
            )),
            Cell::from(Span::styled(status, Style::default().fg(row_color))),
            Cell::from(peak_mem),
            Cell::from(peak_cpu),
        ])
    });

    let title = if is_focused {
        "Results [FOCUSED]"
    } else {
        "Results"
    };
    let border_style = if is_focused {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(6),  // ID
            Constraint::Length(8),  // Job ID
            Constraint::Length(5),  // Run
            Constraint::Length(7),  // Return
            Constraint::Length(12), // Status
            Constraint::Length(10), // Peak Mem
            Constraint::Length(10), // Peak CPU
        ],
    )
    .header(header)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style),
    )
    .row_highlight_style(selected_style)
    .highlight_symbol(">> ");

    f.render_stateful_widget(table, area, &mut app.results_state);
}

fn draw_scheduled_nodes_table(f: &mut Frame, area: Rect, app: &mut App) {
    let is_focused = app.focus == Focus::Details;
    let selected_style = Style::default()
        .add_modifier(Modifier::REVERSED)
        .fg(Color::Cyan);
    let header_style = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);

    let header = Row::new(vec!["ID", "Scheduler ID", "Config ID", "Type", "Status"])
        .style(header_style)
        .bottom_margin(1);

    let rows = app.scheduled_nodes.iter().map(|node| {
        let id = node.id.map(|i| i.to_string()).unwrap_or_default();
        let scheduler_id = node.scheduler_id.to_string();
        let config_id = node.scheduler_config_id.to_string();
        let scheduler_type = node.scheduler_type.clone();
        let status = node.status.clone();

        // Color based on status
        let status_color = match status.as_str() {
            "running" => Color::Green,
            "pending" | "scheduled" => Color::Yellow,
            "failed" | "error" => Color::Red,
            "completed" | "done" => Color::Blue,
            _ => Color::White,
        };

        Row::new(vec![
            Cell::from(id),
            Cell::from(scheduler_id),
            Cell::from(config_id),
            Cell::from(scheduler_type),
            Cell::from(Span::styled(status, Style::default().fg(status_color))),
        ])
    });

    let title = if is_focused {
        "Scheduled Nodes [FOCUSED]"
    } else {
        "Scheduled Nodes"
    };
    let border_style = if is_focused {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(8),  // ID
            Constraint::Length(14), // Scheduler ID
            Constraint::Length(10), // Config ID
            Constraint::Length(10), // Type
            Constraint::Length(12), // Status
        ],
    )
    .header(header)
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style),
    )
    .row_highlight_style(selected_style)
    .highlight_symbol(">> ");

    f.render_stateful_widget(table, area, &mut app.scheduled_nodes_state);
}

fn draw_filter_input(f: &mut Frame, area: Rect, app: &App) {
    let columns = app.get_filter_columns();
    let selected_column = columns[app.filter_column_index];

    let filter_status = if let Some(ref filter) = app.filter {
        format!(
            " | Active filter: {} contains '{}'",
            filter.column, filter.value
        )
    } else {
        String::new()
    };

    let text = vec![Line::from(vec![
        Span::styled("Filter by ", Style::default().fg(Color::White)),
        Span::styled(
            selected_column,
            Style::default()
                .fg(Color::Yellow)
                .add_modifier(Modifier::BOLD),
        ),
        Span::styled(": ", Style::default().fg(Color::White)),
        Span::styled(&app.filter_input, Style::default().fg(Color::Cyan)),
        Span::styled(" | ", Style::default().fg(Color::DarkGray)),
        Span::styled("Tab", Style::default().fg(Color::Yellow)),
        Span::styled(": change column | ", Style::default().fg(Color::White)),
        Span::styled("Enter", Style::default().fg(Color::Yellow)),
        Span::styled(": apply | ", Style::default().fg(Color::White)),
        Span::styled("Esc", Style::default().fg(Color::Yellow)),
        Span::styled(": cancel", Style::default().fg(Color::White)),
        Span::styled(&filter_status, Style::default().fg(Color::DarkGray)),
    ])];

    let block = Block::default()
        .borders(Borders::ALL)
        .title("Filter Input")
        .border_style(Style::default().fg(Color::Green));

    let paragraph = ratatui::widgets::Paragraph::new(text)
        .block(block)
        .style(Style::default().fg(Color::White));

    f.render_widget(paragraph, area);
}

fn draw_server_url_input(f: &mut Frame, area: Rect, app: &App) {
    let text = vec![Line::from(vec![
        Span::styled("Server URL: ", Style::default().fg(Color::White)),
        Span::styled(&app.server_url_input, Style::default().fg(Color::Cyan)),
        Span::styled(" | ", Style::default().fg(Color::DarkGray)),
        Span::styled("Enter", Style::default().fg(Color::Yellow)),
        Span::styled(": connect | ", Style::default().fg(Color::White)),
        Span::styled("Esc", Style::default().fg(Color::Yellow)),
        Span::styled(": cancel", Style::default().fg(Color::White)),
    ])];

    let block = Block::default()
        .borders(Borders::ALL)
        .title("Change Server URL")
        .border_style(Style::default().fg(Color::Green));

    let paragraph = ratatui::widgets::Paragraph::new(text)
        .block(block)
        .style(Style::default().fg(Color::White));

    f.render_widget(paragraph, area);
}

fn draw_user_input(f: &mut Frame, area: Rect, app: &App) {
    let text = vec![Line::from(vec![
        Span::styled("Username: ", Style::default().fg(Color::White)),
        Span::styled(&app.user_input, Style::default().fg(Color::Cyan)),
        Span::styled(" | ", Style::default().fg(Color::DarkGray)),
        Span::styled("Enter", Style::default().fg(Color::Yellow)),
        Span::styled(": apply | ", Style::default().fg(Color::White)),
        Span::styled("Esc", Style::default().fg(Color::Yellow)),
        Span::styled(
            ": cancel | Leave empty for all users",
            Style::default().fg(Color::DarkGray),
        ),
    ])];

    let block = Block::default()
        .borders(Borders::ALL)
        .title("Change User Filter")
        .border_style(Style::default().fg(Color::Green));

    let paragraph = ratatui::widgets::Paragraph::new(text)
        .block(block)
        .style(Style::default().fg(Color::White));

    f.render_widget(paragraph, area);
}

fn draw_workflow_path_input(f: &mut Frame, area: Rect, app: &App) {
    let text = vec![Line::from(vec![
        Span::styled("Workflow spec file: ", Style::default().fg(Color::White)),
        Span::styled(&app.workflow_path_input, Style::default().fg(Color::Cyan)),
        Span::styled("_", Style::default().fg(Color::White)),
        Span::styled(" | ", Style::default().fg(Color::DarkGray)),
        Span::styled("Enter", Style::default().fg(Color::Yellow)),
        Span::styled(": create | ", Style::default().fg(Color::White)),
        Span::styled("Esc", Style::default().fg(Color::Yellow)),
        Span::styled(": cancel", Style::default().fg(Color::White)),
        Span::styled(
            " (supports ~, YAML/JSON/JSON5)",
            Style::default().fg(Color::DarkGray),
        ),
    ])];

    let block = Block::default()
        .borders(Borders::ALL)
        .title("Create Workflow from Spec File")
        .border_style(Style::default().fg(Color::Green));

    let paragraph = ratatui::widgets::Paragraph::new(text)
        .block(block)
        .style(Style::default().fg(Color::White));

    f.render_widget(paragraph, area);
}

fn draw_dag(f: &mut Frame, area: Rect, app: &App) {
    let is_focused = app.focus == Focus::Details;
    let title = if is_focused {
        "Job DAG [FOCUSED]"
    } else {
        "Job DAG"
    };
    let border_style = if is_focused {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    };

    if let Some(ref dag) = app.dag {
        // Build a text-based representation of the DAG
        let mut lines = Vec::new();

        // Compute layers for topological display
        let layers = dag_compute_layers(&dag.graph);

        // Display jobs layer by layer (top to bottom)
        for (layer_idx, layer) in layers.iter().enumerate() {
            if layer_idx > 0 {
                // Add a visual separator between layers showing flow direction
                lines.push(Line::from(vec![Span::styled(
                    "   ↓↓↓",
                    Style::default().fg(Color::DarkGray),
                )]));
            }

            // Display all jobs in this layer
            for &node_idx in layer {
                let node_data = &dag.graph[node_idx];

                // Determine color based on status
                let color = match node_data.status.as_deref() {
                    Some("Completed") => Color::Green,
                    Some("Running") => Color::Yellow,
                    Some("Failed") => Color::Red,
                    Some("Canceled") => Color::Magenta,
                    _ => Color::Cyan,
                };

                // Create a status indicator
                let status_char = match node_data.status.as_deref() {
                    Some("Completed") => "✓",
                    Some("Running") => "▶",
                    Some("Failed") => "✗",
                    Some("Canceled") => "○",
                    _ => "◦",
                };

                // Format: [status] job_name (id: job_id)
                let job_line = format!(
                    "  [{}] {} (id: {})",
                    status_char, node_data.name, node_data.id
                );

                lines.push(Line::from(vec![Span::styled(
                    job_line,
                    Style::default().fg(color),
                )]));
            }
        }

        if lines.is_empty() {
            lines.push(Line::from(vec![Span::styled(
                "No jobs in DAG",
                Style::default().fg(Color::DarkGray),
            )]));
        }

        let block = Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style);

        let paragraph = ratatui::widgets::Paragraph::new(lines)
            .block(block)
            .style(Style::default().fg(Color::White))
            .wrap(ratatui::widgets::Wrap { trim: false });

        f.render_widget(paragraph, area);
    } else {
        // No DAG loaded yet
        let text = vec![Line::from(vec![Span::styled(
            "No DAG data available. Press Enter to load.",
            Style::default().fg(Color::DarkGray),
        )])];

        let block = Block::default()
            .borders(Borders::ALL)
            .title(title)
            .border_style(border_style);

        let paragraph = ratatui::widgets::Paragraph::new(text)
            .block(block)
            .style(Style::default().fg(Color::White))
            .alignment(ratatui::layout::Alignment::Center);

        f.render_widget(paragraph, area);
    }
}

// Helper function to compute layers for DAG visualization
fn dag_compute_layers(
    graph: &petgraph::Graph<super::dag::JobNode, ()>,
) -> Vec<Vec<petgraph::graph::NodeIndex>> {
    use petgraph::visit::{EdgeRef, Topo};
    use std::collections::HashMap;

    let mut layers: Vec<Vec<petgraph::graph::NodeIndex>> = Vec::new();
    let mut node_layer: HashMap<petgraph::graph::NodeIndex, usize> = HashMap::new();

    // Topological traversal
    let mut topo = Topo::new(graph);
    while let Some(node) = topo.next(graph) {
        // Find the maximum layer of all predecessors
        let mut max_predecessor_layer = 0;
        for edge in graph.edges_directed(node, petgraph::Direction::Incoming) {
            if let Some(&layer) = node_layer.get(&edge.source()) {
                max_predecessor_layer = max_predecessor_layer.max(layer + 1);
            }
        }

        node_layer.insert(node, max_predecessor_layer);

        // Add to appropriate layer
        while layers.len() <= max_predecessor_layer {
            layers.push(Vec::new());
        }
        layers[max_predecessor_layer].push(node);
    }

    layers
}
