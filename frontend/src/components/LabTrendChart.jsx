import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function LabTrendChart({ labTrend }) {
  const data = labTrend.map((r) => ({
    date: r.date.slice(0, 7), // YYYY-MM
    phe: r.phe_level_umol_L,
  }));

  return (
    <div className="card chart-card">
      <h3>Phe level trend (umol/L)</h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid stroke="#EDEAE2" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#5C6B6E" }}
            axisLine={{ stroke: "#DEDAD2" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#5C6B6E" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              fontSize: 12,
              fontFamily: "IBM Plex Mono, monospace",
              borderRadius: 6,
              border: "1px solid #DEDAD2",
            }}
          />
          <Line
            type="monotone"
            dataKey="phe"
            stroke="#0E6E66"
            strokeWidth={2}
            dot={{ r: 3, fill: "#0E6E66" }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
