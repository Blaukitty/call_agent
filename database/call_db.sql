
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20) NOT NULL UNIQUE,
    trial VARCHAR(50) DEFAULT 'Стандарт',
    status VARCHAR(50) DEFAULT 'new',
    stop_list BOOLEAN DEFAULT FALSE,
    last_call_date TIMESTAMP,
    callback_date TIMESTAMP,
    call_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS call_sessions (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    result VARCHAR(100),
    script_step VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS scripts (
    id SERIAL PRIMARY KEY,
    step_name VARCHAR(50) UNIQUE NOT NULL,
    phrase TEXT NOT NULL,
    next_step VARCHAR(50)
);


INSERT INTO scripts (step_name, phrase, next_step) VALUES
('greeting', 'Здравствуйте! Вас беспокоит сервис Доктрина. У вас подключён тариф Стандарт. Хотите узнать о Премиум?', 'wait_answer'),
('ask_upgrade', 'Премиум включает неограниченные звонки и приоритетную поддержку. Подключить?', 'wait_consent'),
('consent_yes', 'Отлично! Подключаю вам Премиум. Спасибо за обращение!', 'end'),
('consent_no', 'Хорошо, спасибо за внимание. Если передумаете, мы перезвоним. До свидания!', 'end'),
('callback_agree', 'Хорошо, перезвоним вам позже. Уточните, когда удобно?', 'wait_callback_time'),
('no_answer', 'К сожалению абонент не ответил. Запланирован повторный звонок.', 'schedule_callback')
ON CONFLICT (step_name) DO NOTHING;


INSERT INTO clients (name, phone, trial, status, stop_list) VALUES
('Иван Петров', '+7(999)123-45-67', 'Стандарт', 'new', FALSE),
('Мария Сидорова', '+7(999)234-56-78', 'Стандарт', 'new', FALSE),
('Алексей Иванов', '+7(999)345-67-89', 'Премиум', 'converted', FALSE)
ON CONFLICT (phone) DO NOTHING;


CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_clients_callback ON clients(callback_date);
CREATE INDEX IF NOT EXISTS idx_sessions_client ON call_sessions(client_id);
