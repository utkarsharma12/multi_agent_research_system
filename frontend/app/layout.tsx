import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "Multi-Agent Research System",
  description:
    "AI-powered research assistant using 5 specialized agents — plan, research, fact-check, summarize, and generate professional reports with Google Gemini.",
  keywords: ["AI research", "multi-agent", "LangGraph", "Gemini", "RAG"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${outfit.variable} font-outfit antialiased`}>
        {children}
      </body>
    </html>
  );
}
