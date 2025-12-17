import React, { useState } from "react";
import "./Upload.css";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) {
      setStatus("Please select a file");
      return;
    }
    setIsLoading(true);
    setStatus("Uploading...");
    const fd = new FormData();
    fd.append("file", file);
    try {
      console.log("Uploading file:", file.name);
      console.log("Current URL:", window.location.href);
      console.log("Posting to:", "/upload");
      
      const res = await fetch("/upload", { method: "POST", body: fd });
      
      console.log("Response status:", res.status);
      console.log("Response headers:", res.headers);
      
      // Check if response is ok before trying to parse JSON
      if (!res.ok) {
        const text = await res.text();
        console.error("Response text:", text);
        console.error("Full error - Status:", res.status, "URL:", res.url);
        setStatus(`Server error (${res.status}): Check console for details`);
        setIsLoading(false);
        return;
      }
      
      // Try to parse JSON
      let json;
      try {
        json = await res.json();
        console.log("Parsed JSON:", json);
      } catch (parseErr) {
        console.error("JSON parse error:", parseErr);
        const text = await res.text();
        setStatus(`Invalid response from server: ${text.substring(0, 100)}`);
        setIsLoading(false);
        return;
      }
      
      setStatus(`Uploaded: ${json.filename}`);
      setFile(null);
    } catch (err) {
      console.error("Upload error:", err);
      setStatus(`Error: ${err.message}`);
    } finally { 
      setIsLoading(false);
    }
  }

  return (
    <div className="upload-container">
      <h2>Upload Document</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".pdf,.txt,.docx,.md"
          onChange={(e) => setFile(e.target.files[0])}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !file}>
          {isLoading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {status && (
        <div className={`status ${status.startsWith("Uploaded") ? "success" : "error"}`}>
          {status}
        </div>
      )}
    </div>
  );
}
        