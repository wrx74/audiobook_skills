# Audiobook Skills

Набор Codex skills для локального создания аудиокниг.

## silero-audiobook-builder

Skill помогает превращать русские тексты и книги FB2 в аудио с помощью Silero TTS. Он описывает безопасный и воспроизводимый процесс:

- выбор и проверка исходного файла;
- короткий тест голоса перед обработкой всей книги;
- подготовка русского текста, ударений, имён и латиницы;
- синтез на CUDA с возобновляемым кэшем;
- MP3 по разделам и единый M4B с главами;
- проверка WAV, MP3 и M4B через FFmpeg/FFprobe;
- контрольные суммы, защищающие исходник и предыдущие образцы;
- отдельные рекомендации по мастерингу длинных аудиокниг.

Проверенный профиль по умолчанию: Silero `v5_5_ru`, голос `xenia`, 48 кГц mono.

## Установка

Скопируйте папку `silero-audiobook-builder` в каталог персональных skills Codex:

```powershell
git clone https://github.com/wrx74/audiobook_skills.git
Copy-Item -Recurse -Force .\audiobook_skills\silero-audiobook-builder $env:USERPROFILE\.codex\skills\silero-audiobook-builder
```

После перезапуска Codex skill будет подключаться автоматически к подходящим запросам. Его также можно вызвать явно:

```text
$silero-audiobook-builder
```

## Состав

- `SKILL.md` — основной рабочий процесс;
- `agents/openai.yaml` — метаданные для интерфейса Codex;
- `references/russian-text-preparation.md` — подготовка русского текста;
- `references/mastering.md` — сборка и мастеринг;
- `references/verification-checklist.md` — итоговая проверка.

Репозиторий не содержит моделей, книг или сгенерированных аудиофайлов.
