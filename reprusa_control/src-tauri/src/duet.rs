use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Debug, Serialize, Deserialize)]
pub struct ConnectResult {
    pub connected: bool,
    pub base_url: String,
    pub session_key: Option<u64>,
    pub message: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DuetStatusSummary {
    pub connected: bool,
    pub machine_name: Option<String>,
    pub state: Option<String>,
    pub axes_homed: Vec<bool>,
    pub axis_positions: Vec<f64>,
    pub raw_response_excerpt: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GcodeExecutionResult {
    pub success: bool,
    pub gcode: String,
    pub reply: String,
    pub buffer_space: Option<u32>,
}

#[derive(Debug, Deserialize)]
struct RrConnectResponse {
    pub err: i32,
    #[serde(rename = "sessionTimeout")]
    pub session_timeout: Option<u32>,
    #[serde(rename = "boardType")]
    pub board_type: Option<String>,
    #[serde(rename = "sessionKey")]
    pub session_key: Option<u64>,
}

#[derive(Debug, Deserialize)]
struct RrGcodeResponse {
    pub buff: Option<u32>,
}

pub fn normalise_base_url(input: &str) -> String {
    let trimmed = input.trim().trim_end_matches('/');

    if trimmed.starts_with("http://") || trimmed.starts_with("https://") {
        trimmed.to_string()
    } else {
        format!("http://{}", trimmed)
    }
}

fn build_client() -> Result<Client, String> {
    Client::builder()
        .timeout(Duration::from_secs(5))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {e}"))
}

pub async fn test_duet_connection(
    base_url: &str,
    password: Option<&str>,
) -> Result<ConnectResult, String> {
    let client = build_client()?;
    let normalised = normalise_base_url(base_url);

    // Request a dedicated session key so this app can authenticate explicitly.
    let url = format!("{}/rr_connect", normalised);

    let mut query: Vec<(&str, &str)> = vec![("sessionKey", "yes")];
    if let Some(pw) = password {
        query.push(("password", pw));
    }

    let response = client
        .get(&url)
        .query(&query)
        .send()
        .await
        .map_err(|e| format!("Could not reach Duet at {url}: {e}"))?;

    let status = response.status();
    let body = response
        .text()
        .await
        .unwrap_or_else(|_| "<failed to read response body>".to_string());

    if !status.is_success() {
        return Err(format!(
            "Duet returned HTTP {} from /rr_connect. Response body: {}",
            status, body
        ));
    }

    let payload: RrConnectResponse = serde_json::from_str(&body)
        .map_err(|e| format!("Failed to parse rr_connect response JSON: {e}. Raw body: {body}"))?;

    if payload.err == 0 {
        Ok(ConnectResult {
            connected: true,
            base_url: normalised,
            session_key: payload.session_key,
            message: format!(
                "Connected to Duet successfully{}",
                payload
                    .board_type
                    .as_ref()
                    .map(|b| format!(" ({b})"))
                    .unwrap_or_default()
            ),
        })
    } else {
        Err(format!(
            "Duet rejected login via rr_connect with err code {}. Raw body: {}",
            payload.err, body
        ))
    }
}

pub async fn fetch_duet_status(
    base_url: &str,
    session_key: Option<u64>,
) -> Result<DuetStatusSummary, String> {
    let client = build_client()?;
    let url = format!("{}/rr_model?key=move", normalise_base_url(base_url));

    let mut request = client.get(&url);
    if let Some(key) = session_key {
        request = request.header("X-Session-Key", key.to_string());
    }

    let response = request
        .send()
        .await
        .map_err(|e| format!("Could not fetch Duet status: {e}"))?;

    if !response.status().is_success() {
        return Err(format!(
            "Duet returned HTTP {} when fetching status",
            response.status()
        ));
    }

    let text = response
        .text()
        .await
        .map_err(|e| format!("Failed reading status response: {e}"))?;

    Ok(DuetStatusSummary {
        connected: true,
        machine_name: None,
        state: None,
        axes_homed: vec![],
        axis_positions: vec![],
        raw_response_excerpt: Some(text.chars().take(500).collect()),
    })
}

pub async fn send_gcode(
    base_url: &str,
    session_key: Option<u64>,
    gcode: &str,
) -> Result<GcodeExecutionResult, String> {
    let client = build_client()?;
    let normalised = normalise_base_url(base_url);

    let gcode_url = format!("{}/rr_gcode", normalised);
    let reply_url = format!("{}/rr_reply", normalised);

    let mut request = client.get(&gcode_url).query(&[("gcode", gcode)]);
    if let Some(key) = session_key {
        request = request.header("X-Session-Key", key.to_string());
    }

    let response = request
        .send()
        .await
        .map_err(|e| format!("Failed sending G-code '{gcode}': {e}"))?;

    let status = response.status();
    let body = response
        .text()
        .await
        .unwrap_or_else(|_| "<failed to read response body>".to_string());

    if !status.is_success() {
        return Err(format!(
            "Duet returned HTTP {} from /rr_gcode. Response body: {}",
            status, body
        ));
    }

    let payload: RrGcodeResponse = serde_json::from_str(&body)
        .map_err(|e| format!("Failed to parse rr_gcode response JSON: {e}. Raw body: {body}"))?;

    let mut reply_request = client.get(&reply_url);
    if let Some(key) = session_key {
        reply_request = reply_request.header("X-Session-Key", key.to_string());
    }

    let reply_response = reply_request
        .send()
        .await
        .map_err(|e| format!("Failed fetching G-code reply: {e}"))?;

    let reply_status = reply_response.status();
    let reply_text = reply_response
        .text()
        .await
        .unwrap_or_else(|_| "<failed to read reply body>".to_string());

    if !reply_status.is_success() {
        return Err(format!(
            "Duet returned HTTP {} from /rr_reply. Response body: {}",
            reply_status, reply_text
        ));
    }

    Ok(GcodeExecutionResult {
        success: true,
        gcode: gcode.to_string(),
        reply: reply_text,
        buffer_space: payload.buff,
    })
}