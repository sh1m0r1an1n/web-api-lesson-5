# 💼 Сравниваем вакансии программистов

🤖 Скрипт парсит данные с **HeadHunter** и **SuperJob**.

📌 Для работы нужен **токен SuperJob** (см. установку).

---

## 📦 **Установка**

### 1. 🐍 **Установите Python**
[Скачайте Python 3.8+](https://www.python.org/downloads/) → запустите установку →  
✅ Обязательно отметьте **Add Python to PATH**.

### 2. 📂 **Скачайте и перейдите в папку с проектом**
**Откройте командную строку**:
- На Windows: `Win + R` → введите `cmd` → нажмите **Enter**.
- На macOS/Linux: откройте **Terminal**.
```bash
cd путь/к/вашей/папке
```

### 3. 📦 **Установите зависимости**
```bash
pip install -r requirements.txt
```

### 4. 🔑 **Получите токен SuperJob**
→ Зарегистрируйтесь на [SuperJob API](https://api.superjob.ru/register)

→ Создайте файл .env в папке проекта:
```ini
SECRET_KEY_SUPERJOB=ваш_токен
```

## ⚡ **Запуск**
```bash
python main.py
```

**Пример вывода:**
```
HeadHunter Moscow
+---------------------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+---------------------+------------------+---------------------+------------------+
| Python              | 1500             | 1200                | 120000           |
| JavaScript          | 900              | 750                 | 95000            |
...
```

## 🔍 **Как это работает?**
1. **Парсинг вакансий** → Скрипт получает данные через API.
2. **Расчет зарплаты** → Учитывает диапазон (from/to) и конвертирует в рубли.
3. **Статистика** → Группирует по языкам → выводит в таблицу.

## 📚 **Цель проекта**
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/). 🚀