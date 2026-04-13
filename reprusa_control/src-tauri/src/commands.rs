use crate::duet::{
    fetch_duet_status, send_gcode, test_duet_connection, ConnectResult, DuetStatusSummary,
    GcodeExecutionResult,
};
use crate::state::SharedAppState;
use tauri::State;

#[tauri::command]
pub async fn connect_duet(
    base_url: String,
    password: Option<String>,
    app_state: State<'_, SharedAppState>,
) -> Result<ConnectResult, String> {
    let cleaned_password = password
        .as_deref()
        .map(str::trim)
        .filter(|s| !s.is_empty());

    let result = test_duet_connection(&base_url, cleaned_password).await?;

    let mut state = app_state.lock().await;
    state.duet.base_url = Some(result.base_url.clone());
    state.duet.connected = true;
    state.duet.password_set = cleaned_password.is_some();
    state.duet.session_key = result.session_key;

    Ok(result)
}

#[tauri::command]
pub async fn disconnect_duet(
    app_state: State<'_, SharedAppState>,
) -> Result<bool, String> {
    let mut state = app_state.lock().await;
    state.duet.connected = false;
    state.duet.base_url = None;
    state.duet.password_set = false;
    state.duet.session_key = None;

    Ok(true)
}

#[tauri::command]
pub async fn get_duet_status(
    app_state: State<'_, SharedAppState>,
) -> Result<DuetStatusSummary, String> {
    let state = app_state.lock().await;

    let base_url = state
        .duet
        .base_url
        .clone()
        .ok_or_else(|| "Duet is not connected yet".to_string())?;

    let session_key = state.duet.session_key;
    drop(state);

    fetch_duet_status(&base_url, session_key).await
}

#[tauri::command]
pub async fn run_gcode(
    gcode: String,
    app_state: State<'_, SharedAppState>,
) -> Result<GcodeExecutionResult, String> {
    let state = app_state.lock().await;

    let base_url = state
        .duet
        .base_url
        .clone()
        .ok_or_else(|| "Duet is not connected yet".to_string())?;

    let session_key = state.duet.session_key;
    drop(state);

    send_gcode(&base_url, session_key, &gcode).await
}

#[tauri::command]
pub async fn home_all(
    app_state: State<'_, SharedAppState>,
) -> Result<GcodeExecutionResult, String> {
    let state = app_state.lock().await;

    let base_url = state
        .duet
        .base_url
        .clone()
        .ok_or_else(|| "Duet is not connected yet".to_string())?;

    let session_key = state.duet.session_key;
    drop(state);

    send_gcode(&base_url, session_key, "G28").await
}

#[tauri::command]
pub async fn home_axis(
    axis: String,
    app_state: State<'_, SharedAppState>,
) -> Result<GcodeExecutionResult, String> {
    let axis = axis.trim().to_uppercase();
    if !matches!(axis.as_str(), "X" | "Y" | "Z") {
        return Err("Axis must be one of X, Y, or Z".to_string());
    }

    let gcode = format!("G28 {}", axis);

    let state = app_state.lock().await;
    let base_url = state
        .duet
        .base_url
        .clone()
        .ok_or_else(|| "Duet is not connected yet".to_string())?;
    let session_key = state.duet.session_key;
    drop(state);

    send_gcode(&base_url, session_key, &gcode).await
}

#[tauri::command]
pub async fn jog_axis(
    axis: String,
    distance_mm: f64,
    feedrate_mm_min: Option<f64>,
    app_state: State<'_, SharedAppState>,
) -> Result<GcodeExecutionResult, String> {
    let axis = axis.trim().to_uppercase();
    if !matches!(axis.as_str(), "X" | "Y" | "Z") {
        return Err("Axis must be one of X, Y, or Z".to_string());
    }

    if !distance_mm.is_finite() {
        return Err("Distance must be a finite number".to_string());
    }

    let feed = feedrate_mm_min.unwrap_or(1200.0);
    if !feed.is_finite() || feed <= 0.0 {
        return Err("Feedrate must be a positive finite number".to_string());
    }

    // Relative move, then restore absolute mode.
    let gcode = format!("G91\nG1 {}{:.3} F{:.1}\nG90", axis, distance_mm, feed);

    let state = app_state.lock().await;
    let base_url = state
        .duet
        .base_url
        .clone()
        .ok_or_else(|| "Duet is not connected yet".to_string())?;
    let session_key = state.duet.session_key;
    drop(state);

    send_gcode(&base_url, session_key, &gcode).await
}

#[tauri::command]
pub async fn get_connection_state(
    app_state: State<'_, SharedAppState>,
) -> Result<serde_json::Value, String> {
    let state = app_state.lock().await;
    serde_json::to_value(&*state).map_err(|e| format!("Failed to serialise state: {e}"))
}