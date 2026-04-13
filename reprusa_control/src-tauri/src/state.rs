use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DuetConnectionInfo {
    pub base_url: Option<String>,
    pub password_set: bool,
    pub connected: bool,
    pub session_key: Option<u64>,
}

impl Default for DuetConnectionInfo {
    fn default() -> Self {
        Self {
            base_url: None,
            password_set: false,
            connected: false,
            session_key: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ControllerConnectionInfo {
    pub base_url: Option<String>,
    pub connected: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AppConnectionState {
    pub duet: DuetConnectionInfo,
    pub controller: ControllerConnectionInfo,
}

pub type SharedAppState = Arc<Mutex<AppConnectionState>>;