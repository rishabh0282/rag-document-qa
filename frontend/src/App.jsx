import React from "react";
import Upload from "./components/Upload";
import Query from "./components/Query";
import "./App.css";

export default function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>RAG Document Q&A</h1>
        <p>Upload documents and ask questions about their content</p>
      </header>
      <main className="app-main">
        <Upload />
        <Query />
      </main>
      <footer className="app-footer">
        <p>Powered by FAISS + Sentence-Transformers + FastAPI</p>
      </footer>
    </div>
  );
}
