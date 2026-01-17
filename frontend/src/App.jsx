import React, { useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const defaultLabels = [
  { name: "dom", contacts: ["Mama", "Tata"], keywords: ["rachunki", "naprawa", "zakupy"] },
  { name: "firma", contacts: ["Szef"], keywords: ["projekt", "faktura", "umowa"] },
  { name: "towarzyskie", contacts: ["Ala"], keywords: ["spotkanie", "kawa", "kino"] }
];

const categoryColors = {
  dom: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  firma: "bg-brand-500/15 text-brand-600 dark:text-brand-300",
  towarzyskie: "bg-pink-500/15 text-pink-700 dark:text-pink-300",
  inne: "bg-slate-500/15 text-slate-600 dark:text-slate-300"
};

const useStoredState = (key, initial) => {
  const [state, setState] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initial;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);

  return [state, setState];
};

const buildMarkdown = (tasks) => {
  const grouped = tasks.reduce((acc, task) => {
    const key = `${task.category} — ${task.contact}`;
    acc[key] = acc[key] || [];
    acc[key].push(task);
    return acc;
  }, {});

  return Object.entries(grouped)
    .map(([title, items]) => {
      const list = items.map((task) => `- ${task.text}`).join("\n");
      return `## ${title}\n${list}`;
    })
    .join("\n\n");
};

const swipeThreshold = 80;

const TaskRow = ({ task, onToggle, onDelete }) => {
  const [offset, setOffset] = useState(0);
  const [dragging, setDragging] = useState(false);

  const handleTouchStart = (event) => {
    setDragging(true);
    setOffset(0);
    event.currentTarget.dataset.startX = event.touches[0].clientX;
  };

  const handleTouchMove = (event) => {
    if (!dragging) return;
    const startX = Number(event.currentTarget.dataset.startX || 0);
    const delta = event.touches[0].clientX - startX;
    if (delta < 0) {
      setOffset(Math.max(delta, -120));
    }
  };

  const handleTouchEnd = () => {
    setDragging(false);
    if (Math.abs(offset) > swipeThreshold) {
      onDelete(task.id);
    }
    setOffset(0);
  };

  return (
    <div className="relative">
      <div className="absolute inset-0 flex items-center justify-end pr-4 text-sm text-white bg-rose-500 rounded-xl">
        Usuń
      </div>
      <div
        className="card px-4 py-3 flex items-start gap-3 transition-transform"
        style={{ transform: `translateX(${offset}px)` }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggle(task.id)}
          className="mt-1 h-5 w-5 accent-brand-500"
        />
        <div className="flex-1">
          <p className={`text-sm ${task.completed ? "line-through text-slate-400" : ""}`}>
            {task.text}
          </p>
          <div className="flex flex-wrap gap-2 mt-2 text-xs">
            <span className={`px-2 py-1 rounded-full ${categoryColors[task.category] || categoryColors.inne}`}>
              {task.category}
            </span>
            <span className="px-2 py-1 rounded-full bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {task.contact}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

const LoginView = ({ onLogin }) => {
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("demo123");
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      if (!response.ok) {
        throw new Error("Nieprawidłowe dane logowania");
      }
      const data = await response.json();
      onLogin(data.access_token);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-full flex flex-col justify-center px-6 py-12">
      <div className="card p-8 max-w-md w-full mx-auto">
        <h1 className="text-2xl font-semibold mb-2">Witaj ponownie</h1>
        <p className="text-sm text-slate-500 mb-6">Zaloguj się, aby kontynuować.</p>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            className="w-full rounded-xl border border-slate-200 px-4 py-3 bg-white dark:bg-slate-900 dark:border-slate-700"
            placeholder="Nazwa użytkownika"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
          <input
            type="password"
            className="w-full rounded-xl border border-slate-200 px-4 py-3 bg-white dark:bg-slate-900 dark:border-slate-700"
            placeholder="Hasło"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          {error && <p className="text-sm text-rose-500">{error}</p>}
          <button
            type="submit"
            className="w-full rounded-xl bg-brand-600 text-white py-3 font-medium"
          >
            Zaloguj się
          </button>
        </form>
      </div>
    </div>
  );
};

const Dashboard = ({ token, onLogout }) => {
  const [user, setUser] = useState(null);
  const [labels, setLabels] = useState(defaultLabels);
  const [tasks, setTasks] = useState([]);
  const [markdown, setMarkdown] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useStoredState("darkMode", false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const headers = useMemo(
    () => ({ Authorization: `Bearer ${token}` }),
    [token]
  );

  const fetchProfile = async () => {
    const response = await fetch(`${API_URL}/api/auth/me`, { headers });
    if (!response.ok) return;
    setUser(await response.json());
  };

  const fetchLabels = async () => {
    const response = await fetch(`${API_URL}/api/labels`, { headers });
    if (!response.ok) return;
    const data = await response.json();
    setLabels(data.labels || defaultLabels);
  };

  const fetchTasks = async () => {
    const response = await fetch(`${API_URL}/api/tasks`, { headers });
    if (!response.ok) return;
    const data = await response.json();
    setTasks(data.tasks || []);
  };

  useEffect(() => {
    fetchProfile();
    fetchLabels();
    fetchTasks();
  }, []);

  useEffect(() => {
    const wsUrl = API_URL.replace("http", "ws") + `/ws/tasks?token=${token}`;
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "tasks") {
        setTasks(message.payload.tasks || []);
      }
      if (message.type === "labels") {
        setLabels(message.payload.labels || []);
      }
    };
    return () => ws.close();
  }, [token]);

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${API_URL}/api/summarize`, {
      method: "POST",
      headers,
      body: form
    });
    const data = await response.json();
    setTasks(data.tasks || []);
    setMarkdown(data.markdown || "");
    setLoading(false);
  };

  const handleLabelChange = (index, field, value) => {
    const updated = [...labels];
    updated[index] = { ...updated[index], [field]: value.split(",").map((item) => item.trim()).filter(Boolean) };
    setLabels(updated);
  };

  const addLabel = () => {
    setLabels([...labels, { name: "nowa", contacts: [], keywords: [] }]);
  };

  const saveLabels = async () => {
    await fetch(`${API_URL}/api/labels`, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({ labels })
    });
  };

  const updateTasks = async (nextTasks) => {
    setTasks(nextTasks);
    await fetch(`${API_URL}/api/tasks`, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify(nextTasks)
    });
  };

  const toggleTask = (id) => {
    const nextTasks = tasks.map((task) =>
      task.id === id ? { ...task, completed: !task.completed } : task
    );
    updateTasks(nextTasks);
  };

  const deleteTask = (id) => {
    const nextTasks = tasks.filter((task) => task.id !== id);
    updateTasks(nextTasks);
  };

  const shareTasks = async () => {
    const content = markdown || buildMarkdown(tasks);
    if (navigator.share) {
      await navigator.share({ title: "Podsumowanie zadań", text: content });
    } else {
      await navigator.clipboard.writeText(content);
      alert("Skopiowano do schowka");
    }
  };

  const counts = tasks.reduce(
    (acc, task) => ({ ...acc, [task.category]: (acc[task.category] || 0) + 1 }),
    {}
  );

  return (
    <div className="min-h-full">
      <header className="sticky top-0 z-10 backdrop-blur bg-white/80 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Dashboard</p>
            <h1 className="text-2xl font-semibold">
              <span className="gradient-text">WhatsApp Task Summarizer</span>
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <button
              className="rounded-full border border-slate-200 dark:border-slate-800 px-3 py-2 text-sm"
              onClick={() => setDarkMode((prev) => !prev)}
            >
              {darkMode ? "Jasny" : "Ciemny"}
            </button>
            <button
              className="rounded-full border border-slate-200 dark:border-slate-800 px-3 py-2 text-sm"
              onClick={onLogout}
            >
              Wyloguj
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        <section className="grid gap-4 md:grid-cols-3">
          {["dom", "firma", "towarzyskie", "inne"].map((category) => (
            <div key={category} className="card p-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-400">{category}</p>
                <p className="text-2xl font-semibold">{counts[category] || 0}</p>
              </div>
              <span className={`px-3 py-2 rounded-full text-xs ${categoryColors[category]}`}>
                {category}
              </span>
            </div>
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          <div className="card p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Import wiadomości</h2>
                <p className="text-sm text-slate-500">Wgraj eksport TXT z WhatsApp.</p>
              </div>
              <div className="text-xs text-slate-400">Zalogowany: {user?.username}</div>
            </div>
            <label className="border border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-6 flex flex-col items-center text-center gap-3 cursor-pointer">
              <input type="file" accept=".txt" className="hidden" onChange={handleUpload} />
              <span className="text-sm">Przeciągnij lub dotknij, aby wgrać plik</span>
              {loading && <span className="text-xs text-brand-500">Analizuję wiadomości...</span>}
            </label>
            <button
              className="w-full rounded-xl bg-brand-600 text-white py-3"
              onClick={shareTasks}
            >
              Udostępnij / eksportuj
            </button>
          </div>

          <div className="card p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Etykiety</h2>
              <button className="text-sm text-brand-500" onClick={addLabel}>
                Dodaj
              </button>
            </div>
            <div className="space-y-3 max-h-64 overflow-auto">
              {labels.map((label, index) => (
                <div key={`${label.name}-${index}`} className="space-y-2">
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm dark:bg-slate-900 dark:border-slate-700"
                    value={label.name}
                    onChange={(event) => {
                      const updated = [...labels];
                      updated[index] = { ...label, name: event.target.value };
                      setLabels(updated);
                    }}
                  />
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs dark:bg-slate-900 dark:border-slate-700"
                    placeholder="Kontakty (oddzielone przecinkami)"
                    value={label.contacts.join(", ")}
                    onChange={(event) => handleLabelChange(index, "contacts", event.target.value)}
                  />
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs dark:bg-slate-900 dark:border-slate-700"
                    placeholder="Słowa kluczowe (oddzielone przecinkami)"
                    value={label.keywords.join(", ")}
                    onChange={(event) => handleLabelChange(index, "keywords", event.target.value)}
                  />
                </div>
              ))}
            </div>
            <button className="w-full rounded-xl border border-slate-200 dark:border-slate-700 py-2" onClick={saveLabels}>
              Zapisz etykiety
            </button>
          </div>
        </section>

        <section className="card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Lista zadań</h2>
            <span className="text-xs text-slate-400">Swipe w lewo, aby usunąć</span>
          </div>
          <div className="space-y-3">
            {tasks.length === 0 && (
              <p className="text-sm text-slate-500">Brak zadań. Wgraj plik lub dodaj ręcznie.</p>
            )}
            {tasks.map((task) => (
              <TaskRow key={task.id} task={task} onToggle={toggleTask} onDelete={deleteTask} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default function App() {
  const [token, setToken] = useStoredState("token", "");

  if (!token) {
    return <LoginView onLogin={setToken} />;
  }

  return <Dashboard token={token} onLogout={() => setToken("")} />;
}
