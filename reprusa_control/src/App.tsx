import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";

function App() {
  const [duetUrl, setDuetUrl] = useState("http://192.168.8.100");
  const [duetPassword, setDuetPassword] = useState("");
  const [connectionResult, setConnectionResult] = useState("");
  const [statusResult, setStatusResult] = useState("");

  async function testDuetConnect() {
    try {
      const result = await invoke("connect_duet", {
        baseUrl: duetUrl,
        password: duetPassword.length > 0 ? duetPassword : null,
      });

      setConnectionResult(JSON.stringify(result, null, 2));
    } catch (err) {
      setConnectionResult(`Connection failed: ${String(err)}`);
    }
  }

  async function testDuetStatus() {
    try {
      const result = await invoke("get_duet_status");
      setStatusResult(JSON.stringify(result, null, 2));
    } catch (err) {
      setStatusResult(`Status fetch failed: ${String(err)}`);
    }
  }

  async function runRawGcode(gcode: string) {
    try {
      const result = await invoke("run_gcode", { gcode });
      setStatusResult(JSON.stringify(result, null, 2));
    } catch (err) {
      setStatusResult(`G-code failed: ${String(err)}`);
    }
  }

  async function homeAllAxes() {
    try {
      const result = await invoke("home_all");
      setStatusResult(JSON.stringify(result, null, 2));
    } catch (err) {
      setStatusResult(`Home all failed: ${String(err)}`);
    }
  }

  async function homeSingleAxis(axis: "X" | "Y" | "Z") {
    try {
      const result = await invoke("home_axis", { axis });
      setStatusResult(JSON.stringify(result, null, 2));
    } catch (err) {
      setStatusResult(`Home ${axis} failed: ${String(err)}`);
    }
  }

  async function jogAxis(axis: "X" | "Y" | "Z", distanceMm: number) {
    try {
      const result = await invoke("jog_axis", {
        axis,
        distanceMm,
        feedrateMmMin: 1200,
      });
      setStatusResult(JSON.stringify(result, null, 2));
    } catch (err) {
      setStatusResult(`Jog ${axis} failed: ${String(err)}`);
    }
  }

  return (
    <main style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <h1>RePrusa Control</h1>
      <p>Initial Duet connection test interface</p>

      <div style={{ display: "grid", gap: "0.75rem", marginBottom: "1rem" }}>
        <label>
          Duet URL
          <input
            type="text"
            value={duetUrl}
            onChange={(e) => setDuetUrl(e.target.value)}
            style={{ width: "100%", padding: "0.6rem", marginTop: "0.25rem" }}
          />
        </label>

        <label>
          Duet Password
          <input
            type="password"
            value={duetPassword}
            onChange={(e) => setDuetPassword(e.target.value)}
            placeholder="Leave blank only if no machine password is set"
            style={{ width: "100%", padding: "0.6rem", marginTop: "0.25rem" }}
          />
        </label>
      </div>

      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem" }}>
        <button onClick={testDuetConnect}>Connect to Duet</button>
        <button onClick={testDuetStatus}>Get Duet Status</button>
      </div>

      <div
        style={{
          display: "flex",
          gap: "0.75rem",
          flexWrap: "wrap",
          marginBottom: "1.5rem",
        }}
      >
        <button onClick={homeAllAxes}>G28 Home All</button>
        <button onClick={() => homeSingleAxis("X")}>Home X</button>
        <button onClick={() => homeSingleAxis("Y")}>Home Y</button>
        <button onClick={() => homeSingleAxis("Z")}>Home Z</button>
        <button onClick={() => jogAxis("X", 5)}>X +5</button>
        <button onClick={() => jogAxis("X", -5)}>X -5</button>
        <button onClick={() => jogAxis("Y", 5)}>Y +5</button>
        <button onClick={() => jogAxis("Y", -5)}>Y -5</button>
        <button onClick={() => jogAxis("Z", 1)}>Z +1</button>
        <button onClick={() => jogAxis("Z", -1)}>Z -1</button>
        <button onClick={() => runRawGcode("M115")}>Test M115</button>
      </div>

      <section style={{ marginBottom: "1.5rem" }}>
        <h2>Connection Result</h2>
        <pre>{connectionResult}</pre>
      </section>

      <section>
        <h2>Status Result</h2>
        <pre>{statusResult}</pre>
      </section>
    </main>
  );
}

export default App;