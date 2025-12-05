//! Torc Dashboard - Web UI with CLI integration
//!
//! This binary provides a web dashboard that:
//! - Serves embedded static files (HTML/CSS/JS)
//! - Proxies API requests to a remote torc-server
//! - Executes torc CLI commands locally (for workflow creation, running, submitting)

use anyhow::Result;
use axum::{
    Json, Router,
    body::Body,
    extract::{Path, State},
    http::{Request, StatusCode, header},
    response::{Html, IntoResponse, Response},
    routing::{get, post},
};
use clap::Parser;
use rust_embed::Embed;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::process::Command;
use tower_http::cors::{Any, CorsLayer};
use tracing::{error, info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

/// Embedded static assets for the dashboard
#[derive(Embed)]
#[folder = "static/"]
struct Assets;

/// Application state shared across handlers
#[derive(Clone)]
struct AppState {
    /// URL of the torc-server API
    api_url: String,
    /// HTTP client for proxying requests
    client: reqwest::Client,
    /// Path to the torc CLI binary (defaults to "torc" in PATH)
    torc_bin: String,
}

/// CLI arguments
#[derive(Parser)]
#[command(name = "torc-dash")]
#[command(about = "Torc workflow dashboard with CLI integration")]
struct Cli {
    /// Port to listen on
    #[arg(short, long, default_value_t = 8090)]
    port: u16,

    /// Host to bind to
    #[arg(long, default_value = "127.0.0.1")]
    host: String,

    /// URL of the torc-server API
    #[arg(
        short,
        long,
        default_value = "http://localhost:8080/torc-service/v1",
        env = "TORC_API_URL"
    )]
    api_url: String,

    /// Path to torc CLI binary
    #[arg(long, default_value = "torc", env = "TORC_BIN")]
    torc_bin: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .with(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("torc_dash=info".parse().unwrap()),
        )
        .init();

    let cli = Cli::parse();

    info!("Starting torc-dash on {}:{}", cli.host, cli.port);
    info!("API URL: {}", cli.api_url);
    info!("Torc binary: {}", cli.torc_bin);

    let state = Arc::new(AppState {
        api_url: cli.api_url,
        client: reqwest::Client::new(),
        torc_bin: cli.torc_bin,
    });

    // Build router
    let app = Router::new()
        // Static files and dashboard
        .route("/", get(index_handler))
        .route("/static/*path", get(static_handler))
        // CLI command endpoints
        .route("/api/cli/create", post(cli_create_handler))
        .route("/api/cli/run", post(cli_run_handler))
        .route("/api/cli/submit", post(cli_submit_handler))
        .route("/api/cli/initialize", post(cli_initialize_handler))
        .route(
            "/api/cli/check-initialize",
            post(cli_check_initialize_handler),
        )
        .route("/api/cli/delete", post(cli_delete_handler))
        // API proxy - catch all /torc-service/* requests
        .route(
            "/torc-service/*path",
            get(proxy_handler)
                .post(proxy_handler)
                .put(proxy_handler)
                .patch(proxy_handler)
                .delete(proxy_handler),
        )
        .layer(
            CorsLayer::new()
                .allow_origin(Any)
                .allow_methods(Any)
                .allow_headers(Any),
        )
        .with_state(state);

    let addr = format!("{}:{}", cli.host, cli.port);
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    info!("Dashboard available at http://{}", addr);

    axum::serve(listener, app).await?;

    Ok(())
}

// ============== Static File Handlers ==============

async fn index_handler() -> impl IntoResponse {
    match Assets::get("index.html") {
        Some(content) => Html(content.data.into_owned()).into_response(),
        None => (StatusCode::NOT_FOUND, "index.html not found").into_response(),
    }
}

async fn static_handler(Path(path): Path<String>) -> impl IntoResponse {
    let path = path.trim_start_matches('/');

    match Assets::get(path) {
        Some(content) => {
            let mime = mime_guess::from_path(path).first_or_octet_stream();
            (
                [(header::CONTENT_TYPE, mime.as_ref())],
                content.data.into_owned(),
            )
                .into_response()
        }
        None => (StatusCode::NOT_FOUND, format!("File not found: {}", path)).into_response(),
    }
}

// ============== API Proxy Handler ==============

async fn proxy_handler(
    State(state): State<Arc<AppState>>,
    req: Request<Body>,
) -> impl IntoResponse {
    let path = req.uri().path();
    let query = req
        .uri()
        .query()
        .map(|q| format!("?{}", q))
        .unwrap_or_default();
    let method = req.method().clone();

    // Build the target URL - strip /torc-service/v1 prefix since api_url already contains it
    let target_path = path.strip_prefix("/torc-service/v1").unwrap_or(path);
    let target_url = format!("{}{}{}", state.api_url, target_path, query);

    // Build the proxied request
    let mut proxy_req = state.client.request(method, &target_url);

    // Copy headers
    for (name, value) in req.headers() {
        if name != header::HOST {
            proxy_req = proxy_req.header(name, value);
        }
    }

    // Get body
    let body_bytes = match axum::body::to_bytes(req.into_body(), usize::MAX).await {
        Ok(bytes) => bytes,
        Err(e) => {
            error!("Failed to read request body: {}", e);
            return (
                StatusCode::BAD_REQUEST,
                format!("Failed to read body: {}", e),
            )
                .into_response();
        }
    };

    if !body_bytes.is_empty() {
        proxy_req = proxy_req.body(body_bytes);
    }

    // Execute request
    match proxy_req.send().await {
        Ok(resp) => {
            let status = StatusCode::from_u16(resp.status().as_u16())
                .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);
            let headers = resp.headers().clone();
            let body = resp.bytes().await.unwrap_or_default();

            let mut response = Response::builder().status(status);

            for (name, value) in headers.iter() {
                response = response.header(name, value);
            }

            response.body(Body::from(body)).unwrap().into_response()
        }
        Err(e) => {
            error!("Proxy request failed: {}", e);
            (StatusCode::BAD_GATEWAY, format!("Proxy error: {}", e)).into_response()
        }
    }
}

// ============== CLI Command Handlers ==============

#[derive(Deserialize)]
struct CreateRequest {
    /// Path to workflow spec file OR inline spec content
    spec: String,
    /// If true, spec is file path; if false, spec is inline content
    #[serde(default)]
    is_file: bool,
}

#[derive(Deserialize)]
struct WorkflowIdRequest {
    workflow_id: String,
}

#[derive(Deserialize)]
struct InitializeRequest {
    workflow_id: String,
    #[serde(default)]
    force: bool,
}

#[derive(Serialize)]
struct CliResponse {
    success: bool,
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
}

async fn cli_create_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<CreateRequest>,
) -> impl IntoResponse {
    let result = if req.is_file {
        // Spec is a file path
        run_torc_command(
            &state.torc_bin,
            &["workflows", "create", &req.spec],
            &state.api_url,
        )
        .await
    } else {
        // Spec is inline content - write to temp file
        let temp_path = format!("/tmp/torc_spec_{}.json", std::process::id());
        if let Err(e) = tokio::fs::write(&temp_path, &req.spec).await {
            return Json(CliResponse {
                success: false,
                stdout: String::new(),
                stderr: format!("Failed to write temp file: {}", e),
                exit_code: None,
            });
        }
        let result = run_torc_command(
            &state.torc_bin,
            &["workflows", "create", &temp_path],
            &state.api_url,
        )
        .await;
        let _ = tokio::fs::remove_file(&temp_path).await;
        result
    };

    Json(result)
}

async fn cli_run_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<WorkflowIdRequest>,
) -> impl IntoResponse {
    let result = run_torc_command(
        &state.torc_bin,
        &["workflows", "run", &req.workflow_id],
        &state.api_url,
    )
    .await;
    Json(result)
}

async fn cli_submit_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<WorkflowIdRequest>,
) -> impl IntoResponse {
    let result = run_torc_command(
        &state.torc_bin,
        &["workflows", "submit", &req.workflow_id],
        &state.api_url,
    )
    .await;
    Json(result)
}

async fn cli_initialize_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<InitializeRequest>,
) -> impl IntoResponse {
    let mut args = vec!["workflows", "initialize", &req.workflow_id];
    if req.force {
        args.push("--force");
    }
    let result = run_torc_command(&state.torc_bin, &args, &state.api_url).await;
    Json(result)
}

/// Check initialization status using --dry-run to see if there are existing output files
async fn cli_check_initialize_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<WorkflowIdRequest>,
) -> impl IntoResponse {
    // Run with -f json and --dry-run to get structured output about existing files
    let result = run_torc_command(
        &state.torc_bin,
        &[
            "-f",
            "json",
            "workflows",
            "initialize",
            &req.workflow_id,
            "--dry-run",
        ],
        &state.api_url,
    )
    .await;
    Json(result)
}

async fn cli_delete_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<WorkflowIdRequest>,
) -> impl IntoResponse {
    let result = run_torc_command(
        &state.torc_bin,
        &["workflows", "delete", "--no-prompts", &req.workflow_id],
        &state.api_url,
    )
    .await;
    Json(result)
}

/// Execute a torc CLI command
async fn run_torc_command(torc_bin: &str, args: &[&str], api_url: &str) -> CliResponse {
    info!("Running: {} {}", torc_bin, args.join(" "));

    let output = Command::new(torc_bin)
        .args(args)
        .env("TORC_API_URL", api_url)
        .output()
        .await;

    match output {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            let success = output.status.success();

            if !success {
                warn!("Command failed: {} {}", torc_bin, args.join(" "));
                warn!("stderr: {}", stderr);
            }

            CliResponse {
                success,
                stdout,
                stderr,
                exit_code: output.status.code(),
            }
        }
        Err(e) => {
            error!("Failed to execute command: {}", e);
            CliResponse {
                success: false,
                stdout: String::new(),
                stderr: format!("Failed to execute command: {}", e),
                exit_code: None,
            }
        }
    }
}
