import type { Metadata } from "next";
import { Commissioner, Fraunces } from "next/font/google";
import { ReactNode } from "react";

import { Providers } from "@/components/providers";
import "@/app/globals.css";

const headingFont = Fraunces({
  subsets: ["latin"],
  variable: "--font-heading",
});

const bodyFont = Commissioner({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "Script Insights",
  description: "Multi-agent analysis workspace for script intelligence",
};

type Props = {
  children: ReactNode;
};

export default function RootLayout({ children }: Props) {
  return (
    <html lang="en">
      <body className={`${headingFont.variable} ${bodyFont.variable}`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
