use anyhow::Result;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(about = "Interactive terminal UI for managing workflows", long_about = None)]
pub struct Args {
    /// Start in standalone mode: automatically start a torc-server
    #[arg(long)]
    pub standalone: bool,

    /// Port for the server in standalone mode (default: 8080)
    #[arg(long, default_value = "8080")]
    pub port: u16,

    /// Database path for standalone mode
    #[arg(long)]
    pub database: Option<String>,
}

pub fn run(args: &Args) -> Result<()> {
    // Initialize the TUI
    // The TUI code will be in the optional 'tui' module
    #[cfg(feature = "tui")]
    {
        crate::tui::run(args.standalone, args.port, args.database.clone())
    }

    #[cfg(not(feature = "tui"))]
    {
        let _ = args; // Suppress unused warning
        eprintln!("Error: TUI support was not compiled into this binary");
        eprintln!("Please rebuild with --features tui or use the standalone torc-tui binary");
        std::process::exit(1);
    }
}
