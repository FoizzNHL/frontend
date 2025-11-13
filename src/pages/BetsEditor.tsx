import React, { useEffect, useState } from "react";
import { getBets, saveBets, type BetsFile } from "../lib/nhl/api";

export default function BetsEditor() {
  const [rawJson, setRawJson] = useState<string>("{\n  \"bets\": []\n}");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  // Load from backend
  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        setInfo(null);

        const json: BetsFile = await getBets();
        setRawJson(JSON.stringify(json, null, 2));
        setInfo("Loaded bets from backend.");
      } catch (e: any) {
        setError(e?.message || String(e));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const handleFormat = () => {
    try {
      setError(null);
      const parsed = JSON.parse(rawJson);
      setRawJson(JSON.stringify(parsed, null, 2));
      setInfo("JSON is valid and has been formatted.");
    } catch (e: any) {
      setError("Invalid JSON: " + (e?.message || String(e)));
      setInfo(null);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setInfo(null);

      const parsed = JSON.parse(rawJson) as BetsFile;

      if (!parsed || typeof parsed !== "object") {
        throw new Error("JSON must be an object.");
      }
      if (!Array.isArray(parsed.bets)) {
        throw new Error('JSON must contain a "bets" array.');
      }

      const result = await saveBets(parsed);

      if (!result.ok) {
        throw new Error(result.error || "Failed to save bets.json");
      }

      setRawJson(JSON.stringify(parsed, null, 2));
      setInfo("Saved bets.json on the backend 🎉");
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl p-6 space-y-4">
      <h1 className="text-2xl font-bold mb-2">Bets JSON Editor</h1>
      <p className="text-sm text-gray-600">
        Paste or edit the content of <code>bets.json</code> here and click{" "}
        <strong>Save</strong> to update it on the backend.
      </p>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleFormat}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium shadow hover:opacity-90 transition disabled:opacity-50"
          disabled={loading || saving}
        >
          {loading ? "Loading…" : "Validate & Format JSON"}
        </button>

        <button
          onClick={handleSave}
          className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium shadow hover:opacity-90 transition disabled:opacity-50"
          disabled={loading || saving}
        >
          {saving ? "Saving…" : "Save to backend"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-300 bg-red-50 text-red-700 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {info && !error && (
        <div className="rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-700 px-4 py-3 text-sm">
          {info}
        </div>
      )}

      <textarea
        value={rawJson}
        onChange={(e) => {
          setRawJson(e.target.value);
          setError(null);
          setInfo(null);
        }}
        className="w-full h-[60vh] font-mono text-sm border border-gray-300 text-black rounded-xl p-3 bg-white/90 shadow-inner focus:ring-2 focus:ring-blue-400 focus:outline-none"
        placeholder='{"bets": [ ... ]}'
      />
    </div>
  );
}
