import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AltFlex | AI-Powered Forensic Framework for Web3 Security",
  description:
    "Detect and analyze security exploits in cross-chain bridges and DeFi protocols with advanced machine learning anomaly detection and blockchain forensic analysis.",
  keywords: [
    "DeFi Security",
    "Web3",
    "Blockchain",
    "Exploit Detection",
    "Machine Learning",
    "Forensic Analysis",
    "Flash Loan Detection",
    "Smart Contract Security",
  ],
  authors: [{ name: "AltFlex Team" }],
  openGraph: {
    title: "AltFlex | AI-Powered Forensic Framework for Web3 Security",
    description:
      "Detect and analyze security exploits in cross-chain bridges and DeFi protocols.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
