"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  ["Dashboard", "/dashboard"],
  ["Restaurants", "/restaurants"],
  ["Customers", "/customers"],
  ["Menu", "/menu"],
  ["Orders", "/orders"],
  ["Campaigns", "/campaigns"],
  ["Items", "/items"],
  ["Accounting", "/accounting"],
  ["AI", "/ai"]
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <img src="/joeai-logo.svg" className="logo" />

      <nav>
        {links.map(([label, href]) => (
          <Link
            key={href}
            href={href}
            className={pathname === href ? "nav active" : "nav"}
          >
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
