import Link from "next/link";

const features = [
  {
    title: "Live Nutrition Tracking",
    description: "See calories, sugar, protein, and caffeine update instantly as you customize your drink.",
    href: "/customize",
    icon: "🥤",
  },
  {
    title: "Smart Barista Queue",
    description: "Prioritize drive-thru, batch similar drinks, and track orders from mobile, walk-in, and drive-thru.",
    href: "/barista",
    icon: "📋",
  },
  {
    title: "Operations Analytics",
    description: "Monitor rush alerts, average wait times, and order volume by channel in real time.",
    href: "/analytics",
    icon: "📊",
  },
];

export default function HomePage() {
  return (
    <div>
      <section className="mb-12 text-center">
        <h1 className="mb-4 text-4xl font-bold text-cafe-green-dark">
          Smart Café Operations & Nutrition Tracker
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-gray-600">
          A full-stack portfolio project solving real store problems: live nutrition transparency
          for customers and intelligent queue management for baristas during rush hours.
        </p>
      </section>

      <div className="grid gap-6 md:grid-cols-3">
        {features.map((feature) => (
          <Link
            key={feature.href}
            href={feature.href}
            className="card group transition hover:border-cafe-green hover:shadow-md"
          >
            <span className="mb-3 block text-3xl">{feature.icon}</span>
            <h2 className="mb-2 text-xl font-semibold text-cafe-green-dark group-hover:text-cafe-green">
              {feature.title}
            </h2>
            <p className="text-sm text-gray-600">{feature.description}</p>
          </Link>
        ))}
      </div>

      <section className="mt-12 rounded-xl bg-cafe-green-dark p-8 text-white">
        <h2 className="mb-4 text-2xl font-bold">Built for Starbucks Engineering</h2>
        <p className="mb-4 max-w-3xl text-white/80">
          This project demonstrates REST API design, real-time nutrition computation, smart queue
          sequencing algorithms, SQLite persistence, and a clean React frontend — skills directly
          applicable to Starbucks mobile ordering and store operations platforms.
        </p>
        <div className="flex flex-wrap gap-2">
          {["FastAPI", "Next.js", "SQLite", "Tailwind CSS", "REST API"].map((tech) => (
            <span key={tech} className="rounded-full bg-white/10 px-3 py-1 text-sm">
              {tech}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
