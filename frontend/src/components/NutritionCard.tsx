interface NutritionCardProps {
  calories: number;
  sugar: number;
  protein: number;
  caffeine: number;
  summary: string;
}

export default function NutritionCard({ calories, sugar, protein, caffeine, summary }: NutritionCardProps) {
  const stats = [
    { label: "Calories", value: calories, unit: "kcal", color: "text-orange-600" },
    { label: "Sugar", value: sugar, unit: "g", color: "text-pink-600" },
    { label: "Protein", value: protein, unit: "g", color: "text-blue-600" },
    { label: "Caffeine", value: caffeine, unit: "mg", color: "text-amber-700" },
  ];

  return (
    <div className="card border-cafe-green/30 bg-cafe-green-light/30">
      <h3 className="mb-4 text-lg font-semibold text-cafe-green-dark">Live Nutrition</h3>
      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg bg-white p-3 text-center shadow-sm">
            <p className="text-xs uppercase tracking-wide text-gray-500">{stat.label}</p>
            <p className={`text-2xl font-bold ${stat.color}`}>
              {stat.value}
              <span className="text-sm font-normal text-gray-500"> {stat.unit}</span>
            </p>
          </div>
        ))}
      </div>
      <p className="rounded-lg bg-white p-3 text-sm font-medium text-cafe-green-dark">{summary}</p>
    </div>
  );
}
