import type { Metadata } from "next";
import "@/styles/globals.css";
import { AuthProvider } from "@/stores/AuthContext";

export const metadata: Metadata = {
  title: "HireAI Local",
  description: "AI Interview & Hiring Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
