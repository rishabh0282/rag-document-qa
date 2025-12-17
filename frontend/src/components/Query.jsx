import React, { useState } from "react";
import "./Query.css";

export default function Query() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleQuery(e) {
    e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a query");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const json = await res.json();
      if (res.ok) {
        setResults(json);
      } else {
        setError(json.detail || "Query failed");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="query-container">
      <h2>Query Documents</h2>
      <form onSubmit={handleQuery}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? "Searching..." : "Ask"}
        </button>
      </form>
      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading">Searching documents...</div>}
      {results && (
        <div className="results">
          <h3>
            Results for: <em>"{results.query}"</em>
          </h3>
          {results.results && results.results.length > 0 ? (
            <div className="results-list">
              {results.results.map((r, i) => (
                <div key={i} className="result-item">
                  <div className="result-header">
                    <span className="result-rank">#{i + 1}</span>
                    <span className="result-score">
                      Relevance: {(Math.max(0, 3 - r.score) / 3) * 100}%
                    </span>
                  </div>
                  <div className="result-filename">
                    ?? {r.metadata.filename.replace(/_[a-f0-9]{32}_/, "")}
                  </div>
                  <div className="result-chunk">Chunk {r.metadata.chunk}</div>
                  {r.metadata.text && (
                    <div className="result-text">
                      "{r.metadata.text.substring(0, 250)}..."
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="no-results">No matching documents found</div>
          )}
        </div>
      )}
    </div>
  );
}
