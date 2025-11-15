use anyhow::Result;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
};
use ratatui::{Terminal, backend::CrosstermBackend};
use std::io;

mod api;
mod app;
mod dag;
mod ui;

use app::App;

pub fn run() -> Result<()> {
    env_logger::init();

    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app and run
    let app = App::new()?;
    let res = run_app(&mut terminal, app);

    // Restore terminal
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        eprintln!("Error: {}", err);
    }

    Ok(())
}

fn run_app<B: ratatui::backend::Backend>(terminal: &mut Terminal<B>, mut app: App) -> Result<()> {
    loop {
        terminal.draw(|f| ui::draw(f, &mut app))?;

        if event::poll(std::time::Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                if key.kind == KeyEventKind::Press {
                    match app.focus {
                        app::Focus::FilterInput => match key.code {
                            KeyCode::Esc => app.cancel_filter(),
                            KeyCode::Enter => app.apply_filter(),
                            KeyCode::Backspace => app.remove_filter_char(),
                            KeyCode::Tab => app.next_filter_column(),
                            KeyCode::BackTab => app.prev_filter_column(),
                            KeyCode::Char(c) => app.add_filter_char(c),
                            _ => {}
                        },
                        app::Focus::ServerUrlInput => match key.code {
                            KeyCode::Esc => app.cancel_server_url_input(),
                            KeyCode::Enter => {
                                if let Err(e) = app.apply_server_url() {
                                    eprintln!("Failed to connect to server: {}", e);
                                    app.cancel_server_url_input();
                                }
                            }
                            KeyCode::Backspace => app.remove_server_url_char(),
                            KeyCode::Char(c) => app.add_server_url_char(c),
                            _ => {}
                        },
                        app::Focus::UserInput => match key.code {
                            KeyCode::Esc => app.cancel_user_input(),
                            KeyCode::Enter => {
                                if let Err(e) = app.apply_user_filter() {
                                    eprintln!("Failed to apply user filter: {}", e);
                                    app.cancel_user_input();
                                }
                            }
                            KeyCode::Backspace => app.remove_user_char(),
                            KeyCode::Char(c) => app.add_user_char(c),
                            _ => {}
                        },
                        _ => match key.code {
                            KeyCode::Char('q') => return Ok(()),
                            KeyCode::Down => app.next_in_active_table(),
                            KeyCode::Up => app.previous_in_active_table(),
                            KeyCode::Enter => {
                                app.load_detail_data()?;
                            }
                            KeyCode::Tab => app.next_detail_view(),
                            KeyCode::BackTab => app.previous_detail_view(),
                            KeyCode::Char('r') => {
                                app.refresh_workflows()?;
                            }
                            KeyCode::Left | KeyCode::Right => {
                                app.toggle_focus();
                            }
                            KeyCode::Char('f') => {
                                if app.focus == app::Focus::Details {
                                    app.start_filter();
                                }
                            }
                            KeyCode::Char('c') => {
                                if app.focus == app::Focus::Details {
                                    app.clear_filter();
                                }
                            }
                            KeyCode::Char('u') => {
                                app.start_server_url_input();
                            }
                            KeyCode::Char('w') => {
                                app.start_user_input();
                            }
                            KeyCode::Char('a') => {
                                if let Err(e) = app.toggle_show_all_users() {
                                    eprintln!("Failed to toggle user filter: {}", e);
                                }
                            }
                            _ => {}
                        },
                    }
                }
            }
        }
    }
}
