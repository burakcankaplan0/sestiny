import { ConnectionStatus } from "./components/ConnectionStatus";
import { useBackendHealth } from "./hooks/useBackendHealth";
import { texts } from "./texts";
import "./App.css";

function App() {
  const { status, message, retry } = useBackendHealth();

  return (
    <div className="page">
      <main className="page__content">
        <header className="intro">
          <p className="intro__eyebrow">{texts.app.tagline}</p>
          <h1 className="intro__title">{texts.app.name}</h1>
          <p className="intro__text">{texts.app.intro}</p>
        </header>

        <ConnectionStatus status={status} message={message} onRetry={retry} />

        <section className="notice" aria-labelledby="notice-title">
          <h2 className="notice__title" id="notice-title">
            {texts.disclaimer.title}
          </h2>
          <p className="notice__text">{texts.disclaimer.notDiagnosis}</p>
          <p className="notice__text">{texts.disclaimer.privacy}</p>
        </section>
      </main>
    </div>
  );
}

export default App;
