mod commands;
mod duet;
mod state;

use state::{AppConnectionState, SharedAppState};
use std::sync::Arc;
use tokio::sync::Mutex;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let shared_state: SharedAppState = Arc::new(Mutex::new(AppConnectionState::default()));

    tauri::Builder::default()
        .manage(shared_state)
        .invoke_handler(tauri::generate_handler![
            commands::connect_duet,
            commands::disconnect_duet,
            commands::get_duet_status,
            commands::run_gcode,
            commands::home_all,
            commands::home_axis,
            commands::jog_axis,
            commands::get_connection_state
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}