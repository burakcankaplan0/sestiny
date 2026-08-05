import type { ReactNode } from "react";

import "../App.css";

interface ScreenLayoutProps {
  eyebrow?: string;
  title: string;
  description?: string;
  children?: ReactNode;
}

/** Tüm akış ekranlarının ortak sayfa iskeleti: üstte başlık bloğu, altında ekrana özel içerik. */
export function ScreenLayout({ eyebrow, title, description, children }: ScreenLayoutProps) {
  return (
    <div className="page">
      <main className="page__content">
        <header className="intro">
          {eyebrow ? <p className="intro__eyebrow">{eyebrow}</p> : null}
          <h1 className="intro__title">{title}</h1>
          {description ? <p className="intro__text">{description}</p> : null}
        </header>
        {children}
      </main>
    </div>
  );
}
