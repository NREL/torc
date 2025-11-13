use std::fmt;

#[derive(Debug)]
pub enum TorcError {
    ApiError(String),
    CommandFailed(String),
    OperationNotAllowed(String),
}

impl fmt::Display for TorcError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TorcError::ApiError(msg) => write!(f, "API error: {}", msg),
            TorcError::CommandFailed(msg) => write!(f, "Command failed: {}", msg),
            TorcError::OperationNotAllowed(msg) => write!(f, "Operation not allowed: {}", msg),
        }
    }
}

impl std::error::Error for TorcError {}
