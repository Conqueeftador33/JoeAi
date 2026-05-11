import "./globals.css";
import Sidebar from "./components/Sidebar";

export const metadata = {
  title: "JoeAI - Restaurant Revenue OS",
  description: "AI restaurant CRM and revenue platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <Sidebar />
          <main className="main-content">{children}</main>
        </div>
      </body>
    </html>
  );
}
