import './globals.css';
import Link from 'next/link';

export const metadata = {
  title: 'PKP Bet',
  description: 'Typowanie opóźnień pociągów IC',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pl">
      <body>
        <header>
          <nav>
            <Link href="/">Dzisiejsze pociągi</Link> | <Link href="/bets">Obstaw</Link> |{' '}
            <Link href="/leaderboard">Ranking</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
