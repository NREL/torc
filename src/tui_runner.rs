use anyhow::Result;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(about = "Interactive terminal UI for managing workflows", long_about = None)]
pub struct Args {
    // TUI doesn't need arguments from CLI, it's all interactive
    // But we keep this struct for consistency
}

pub fn run(_args: &Args) -> Result<()> {
    // Initialize the TUI
    // The TUI code will be in the optional 'tui' module
    #[cfg(feature = "tui")]
    {
        crate::tui::run()
    }

    #[cfg(not(feature = "tui"))]
    {
        eprintln!("Error: TUI support was not compiled into this binary");
        eprintln!("Please rebuild with --features tui or use the standalone torc-tui binary");
        std::process::exit(1);
    }
}
