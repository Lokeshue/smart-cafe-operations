import Link from "next/link";

const links = [
  { href: "/customize", label: "Customize Drink" },
  { href: "/barista", label: "Barista Queue" },
  { href: "/analytics", label: "Analytics" },
];

export default function Navbar() {
  return (
    <nav className="border-b border-cafe-green/20 bg-cafe-green-dark text-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-lg font-bold tracking-tight">
          ☕ Smart Café
        </Link>
        <div className="flex gap-6">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-white/80 transition hover:text-white"
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
