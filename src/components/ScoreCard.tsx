import { getTeamColor } from "../lib/nhl/colors";

export default function ScoreCard({ score }) {
  const awayColor = getTeamColor(score.away?.abbr);
  const homeColor = getTeamColor(score.home?.abbr);

  return (
    <div className="p-6 rounded-2xl bg-white/70 backdrop-blur-md border border-gray-200 shadow-lg relative overflow-hidden">
      <div className="absolute inset-0 bg-linear-to-br from-white/50 to-transparent pointer-events-none" />

      <div className="flex justify-between items-center text-sm text-gray-600">
        <span>{score.date || "Today"}</span>
        <span className="uppercase font-semibold text-gray-700">
          {score.state}
        </span>
      </div>

      <div className="flex items-center justify-center mt-4 text-5xl font-extrabold">
        <span style={{ color: awayColor.primary }}>{score.away?.abbr}</span>
        <span
          className="mx-3"
          style={{
            color:
              score.away?.score > score.home?.score
                ? awayColor.secondary
                : homeColor.secondary,
          }}
        >
          {score.away?.score} – {score.home?.score}
        </span>
        <span style={{ color: homeColor.primary }}>{score.home?.abbr}</span>
      </div>
    </div>
  );
}
