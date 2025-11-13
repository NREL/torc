use tabled::settings::Style;
use tabled::{Table, Tabled};

/// Display a collection of items as a formatted table
pub fn display_table<T: Tabled>(items: &[T]) {
    if items.is_empty() {
        return;
    }

    let mut table = Table::new(items);
    table.with(Style::rounded());
    println!("{}", table);
}

/// Display a collection of items as a formatted table with a custom title
pub fn display_table_with_title<T: Tabled>(items: &[T], title: &str) {
    if items.is_empty() {
        println!("{}", title);
        return;
    }

    println!("{}", title);
    let mut table = Table::new(items);
    table.with(Style::rounded());
    println!("{}", table);
}

/// Display a collection of items as a formatted table with a total count
pub fn display_table_with_count<T: Tabled>(items: &[T], item_type: &str) {
    if items.is_empty() {
        return;
    }

    let mut table = Table::new(items);
    table.with(Style::rounded());
    println!("{}", table);
    println!("\nTotal: {} {}", items.len(), item_type);
}
