//! Dashboard module for serving embedded static web assets.
//!
//! This module provides a web dashboard for Torc that is embedded directly
//! into the server binary, eliminating the need for Python or external files.

use hyper::{Body, Response, StatusCode};
use rust_embed::Embed;

/// Embedded static assets for the dashboard
#[derive(Embed)]
#[folder = "src/server/dashboard/static/"]
pub struct DashboardAssets;

/// MIME type mappings for common file extensions
fn get_mime_type(path: &str) -> &'static str {
    let ext = path.rsplit('.').next().unwrap_or("");
    match ext.to_lowercase().as_str() {
        "html" => "text/html; charset=utf-8",
        "css" => "text/css; charset=utf-8",
        "js" => "application/javascript; charset=utf-8",
        "json" => "application/json; charset=utf-8",
        "png" => "image/png",
        "jpg" | "jpeg" => "image/jpeg",
        "gif" => "image/gif",
        "svg" => "image/svg+xml",
        "ico" => "image/x-icon",
        "woff" => "font/woff",
        "woff2" => "font/woff2",
        "ttf" => "font/ttf",
        "eot" => "application/vnd.ms-fontobject",
        _ => "application/octet-stream",
    }
}

/// Serve a static asset from the embedded dashboard files.
///
/// Returns `Some(Response)` if the path matches a dashboard route,
/// or `None` if the request should be handled by the API.
pub fn serve_dashboard(path: &str) -> Option<Response<Body>> {
    // Normalize path
    let path = path.trim_start_matches('/');

    // Handle root path
    if path.is_empty() || path == "dashboard" || path == "dashboard/" {
        return serve_file("index.html");
    }

    // Handle static files under /static/
    if let Some(static_path) = path.strip_prefix("static/") {
        return serve_file(static_path);
    }

    // For SPA routing, serve index.html for dashboard sub-routes
    // (but not for API routes which start with torc-service)
    if !path.starts_with("torc-service") && !path.contains('.') {
        // This could be a client-side route, serve index.html
        return serve_file("index.html");
    }

    None
}

/// Serve a specific file from embedded assets
fn serve_file(path: &str) -> Option<Response<Body>> {
    match DashboardAssets::get(path) {
        Some(content) => {
            let mime_type = get_mime_type(path);
            let body = Body::from(content.data.into_owned());

            Some(
                Response::builder()
                    .status(StatusCode::OK)
                    .header("Content-Type", mime_type)
                    .header("Cache-Control", "public, max-age=3600")
                    .body(body)
                    .expect("Failed to build response"),
            )
        }
        None => {
            // File not found in embedded assets
            None
        }
    }
}

/// Check if a path is a dashboard route (not an API route)
pub fn is_dashboard_route(path: &str) -> bool {
    let path = path.trim_start_matches('/');

    // Root path
    if path.is_empty() {
        return true;
    }

    // Explicit dashboard routes
    if path == "dashboard" || path.starts_with("dashboard/") {
        return true;
    }

    // Static assets
    if path.starts_with("static/") {
        return true;
    }

    // Favicon
    if path == "favicon.ico" {
        return true;
    }

    false
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_dashboard_route() {
        assert!(is_dashboard_route("/"));
        assert!(is_dashboard_route("/dashboard"));
        assert!(is_dashboard_route("/dashboard/"));
        assert!(is_dashboard_route("/static/css/style.css"));
        assert!(is_dashboard_route("/static/js/app.js"));
        assert!(is_dashboard_route("/favicon.ico"));

        assert!(!is_dashboard_route("/torc-service/v1/workflows"));
        assert!(!is_dashboard_route("/torc-service/v1/jobs"));
    }

    #[test]
    fn test_get_mime_type() {
        assert_eq!(get_mime_type("index.html"), "text/html; charset=utf-8");
        assert_eq!(get_mime_type("style.css"), "text/css; charset=utf-8");
        assert_eq!(
            get_mime_type("app.js"),
            "application/javascript; charset=utf-8"
        );
        assert_eq!(
            get_mime_type("data.json"),
            "application/json; charset=utf-8"
        );
        assert_eq!(get_mime_type("image.png"), "image/png");
    }

    #[test]
    fn test_serve_dashboard_root() {
        let response = serve_dashboard("/");
        assert!(response.is_some());
    }

    #[test]
    fn test_serve_dashboard_static() {
        let response = serve_dashboard("/static/css/style.css");
        assert!(response.is_some());
    }
}
