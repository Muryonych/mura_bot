import React, { useEffect, useState } from "react";
import './index.css';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, BarChart, Bar
} from "recharts";
import { format } from "date-fns";

function App() {
  const [stats, setStats] = useState(null);
  const [chatTitles, setChatTitles] = useState({});
  const [dates, setDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [summary, setSummary] = useState({
    all_time: 0,
    this_month: 0,
    today: 0,
    last_hour: 0
  });

  // Первичное получение статистики и названий бесед
  useEffect(() => {
    fetch("/api/stats")
      .then(res => res.json())
      .then(data => {
        // Сохраняем список дат и названия чатов
        const allDates = Object.keys(data.graphs?.daily || {}).sort().reverse();
        setDates(allDates);
        setChatTitles(data.chat_titles || {});

        // Устанавливаем стартовую дату
        if (!allDates.includes(selectedDate) && allDates.length > 0) {
          setSelectedDate(allDates[0]);
        }

        // Сводка
        if (data.stats) setSummary({
          all_time: data.stats.total || 0,
          this_month: data.stats.month || 0,
          today: data.stats.today || 0,
          last_hour: data.stats.last_hour || 0
        });
      });
  }, []);

  // Подгрузка деталей выбранной даты
  useEffect(() => {
    fetch("/api/stats")           // backend игнорирует query-строку, возвращает всё
      .then(res => res.json())
      .then(data => {
        setStats(data);
      });
  }, [selectedDate]);

  if (!stats) return <div className="p-4 text-gray-200 bg-gray-900">Загрузка...</div>;

  const dayStats = stats.graphs?.daily?.[selectedDate] || { hourly: {}, top_chats: [], total: 0 };

  // hourlyData остаётся без изменений
  const hourlyData = Object.entries(dayStats.hourly).map(
    ([hour, count]) => ({ hour, count })
  );

  // Топ чатов с названием
  const topChats = dayStats.top_chats.map(
    ([id, count]) => ({
      id,
      count,
      title: chatTitles[id]?.title || `Чат ${id}`
    })
  );

  return (
    <div className="App bg-gray-900 text-white min-h-screen p-4">
      <h1 className="text-3xl font-bold mb-6">📊 Статистика обрабатываемых ботом сообщений</h1>

      {/* Сводка */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 p-4 rounded shadow">
          <div className="text-sm">🧠 Всего</div>
          <div className="text-2xl font-semibold">{summary.all_time}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded shadow">
          <div className="text-sm">📅 За месяц</div>
          <div className="text-2xl font-semibold">{summary.this_month}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded shadow">
          <div className="text-sm">📆 Сегодня</div>
          <div className="text-2xl font-semibold">{summary.today}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded shadow">
          <div className="text-sm">⏱ За последний час</div>
          <div className="text-2xl font-semibold">{summary.last_hour}</div>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Выбор даты */}
        <aside className="w-full md:w-60">
          <h2 className="text-lg font-semibold mb-2">📅 Даты</h2>
          <ul>
            {dates.map(date => (
              <li
                key={date}
                onClick={() => setSelectedDate(date)}
                className={`cursor-pointer p-2 rounded mb-1 transition ${
                  selectedDate === date ? "bg-blue-600 text-white" : "hover:bg-gray-700"
                }`}
              >
                {date}
              </li>
            ))}
          </ul>
        </aside>

        {/* Основная часть */}
        <main className="flex-1">
          <h2 className="text-2xl font-semibold mb-4">📆 Статистика за {selectedDate}</h2>
          <p className="mb-4">📨 Всего сообщений за день: {dayStats.total}</p>

          {/* Сообщения по часам */}
          <section className="mb-8">
            <h3 className="text-lg mb-2">⏰ Сообщения по часам</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="hour" stroke="#ccc" />
                <YAxis allowDecimals={false} stroke="#ccc" />
                <Tooltip formatter={(value, name) => [`${value}`, name === 'count' ? 'Сообщений' : name]}/>
                <Line type="monotone" dataKey="count" stroke="#60a5fa" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </section>

          {/* Топ чатов с названиями */}
          <section>
            <h3 className="text-lg mb-2">💬 Топ чатов</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topChats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="title" stroke="#ccc" />
                <YAxis allowDecimals={false} stroke="#ccc" />
                <Tooltip formatter={(value, name) => [`${value}`, name === 'count' ? 'Сообщений' : name]}
      contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', border: 'none', borderRadius: 4 }}
      labelStyle={{ color: '#000000', fontWeight: 'bold', fontSize: 12 }}
      itemStyle={{ color: '#000000', fontSize: 14 }}/>
                <Bar dataKey="count" fill="#34d399" />
              </BarChart>
            </ResponsiveContainer>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
