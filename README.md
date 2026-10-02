# Audiobook Skills

Набор Codex skills для локального создания аудиокниг с Silero TTS и OmniVoice.

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

## Где взять Silero

Официальный проект: [snakers4/silero-models](https://github.com/snakers4/silero-models). Список актуальных моделей и голосов хранится в [models.yml](https://github.com/snakers4/silero-models/blob/master/models.yml).

Сначала установите [PyTorch](https://pytorch.org/get-started/locally/) под свою систему и CUDA. Затем модель можно загрузить через PyTorch Hub:

```python
import torch

model, example_text = torch.hub.load(
    repo_or_dir="snakers4/silero-models",
    model="silero_tts",
    language="ru",
    speaker="v5_5_ru",
)
model.to("cuda")
```

Репозиторий и модель загружаются при первом запуске, затем используются из локального кэша PyTorch. Альтернативный официальный вариант установки:

```powershell
pip install silero
```

Для автономного хранения модель `v5_5_ru` доступна напрямую: [v5_5_ru.pt](https://models.silero.ai/models/tts/ru/v5_5_ru.pt). Голос `xenia` выбирается при синтезе. Сам файл модели, PyTorch и FFmpeg в этот репозиторий не входят.

## omnivoice-audiobook-builder

Skill предназначен для русской озвучки и аудиокниг через OmniVoice в локальном приложении VoiceStudio. Он помогает:

- сохранять один стабильный клонированный голос по всему тексту;
- управлять контекстными паузами и режиссёрской пунктуацией;
- отделять исходный текст от подготовленной версии для синтеза;
- воспроизводимо использовать профиль 48 шагов, seed `42`, 48 кГц mono;
- проверять текст, WAV, параметры модели и полное декодирование результата.

В комплект входит `scripts/render_omnivoice.py`, работающий с локальным API VoiceStudio и формирующий JSON-отчёт проверки.

## Где взять OmniVoice

OmniVoice устанавливается как движок внутри открытого локального приложения [VoiceStudio](https://github.com/debpalash/VoiceStudio). Готовые версии для Windows и других поддерживаемых платформ опубликованы в разделе [VoiceStudio Releases](https://github.com/debpalash/VoiceStudio/releases).

После установки запустите VoiceStudio, выберите или загрузите движок **OmniVoice** в разделе моделей. Skill обращается к локальному API VoiceStudio; проверенная конфигурация использует `http://127.0.0.1:3900`, русский язык и клонирование по WAV-референсу с его точной расшифровкой.

VoiceStudio, модель OmniVoice и голосовые референсы в этот репозиторий не входят.


## Аудиопример

Небольшой диалоговый отрывок из уже собранной аудиокниги «Ложная слепота»:

[Скачать или прослушать sample — около 3 минут](samples/lozhnaya-slepota-dialog-silero-xenia.mp3)

Параметры: Silero `v5_5_ru`, голос `xenia`, русский язык, MP3 mono 48 кГц. Фрагмент приведён для демонстрации качества синтеза и обработки длинной аудиокниги.

### OmniVoice + Silero

[Скачать или прослушать гибридный sample — около 42 секунд](samples/Blindsight-negative-reinforcement-hybrid-Omni-Silero-v1.wav)

Параметры: повествование и Сири — OmniVoice; Саша — Silero `v5_5_ru`, голос `xenia`; WAV PCM mono 48 кГц. Реплики собраны без фейдов, с отдельными голосами персонажей.
### Только OmniVoice

[Скачать или прослушать одноголосый sample с Сарасти — около 2 минут](samples/Blindsight-sarasti-singlevoice-OmniVoice.wav)

Параметры: только OmniVoice, один стабильный голос, 48 шагов; WAV PCM mono 48 кГц. Фрагмент содержит разговор Сири с Сарасти и вампирскую притчу.
## Установка

Клонируйте репозиторий и скопируйте нужные skills в каталог персональных skills Codex:

```powershell
git clone https://github.com/wrx74/audiobook_skills.git
Copy-Item -Recurse -Force .\audiobook_skills\silero-audiobook-builder $env:USERPROFILE\.codex\skills\silero-audiobook-builder
Copy-Item -Recurse -Force .\audiobook_skills\omnivoice-audiobook-builder $env:USERPROFILE\.codex\skills\omnivoice-audiobook-builder
```

После перезапуска Codex skills будут подключаться автоматически к подходящим запросам. Их также можно вызвать явно:

```text
$silero-audiobook-builder
$omnivoice-audiobook-builder
```

## Состав

- `silero-audiobook-builder/` — полный процесс создания аудиокниг с Silero;
- `omnivoice-audiobook-builder/` — направленная озвучка OmniVoice через VoiceStudio;
- `SKILL.md` в каждой папке — основной рабочий процесс;
- `agents/openai.yaml` — метаданные для интерфейса Codex;
- `references/` — инструкции по подготовке текста, API, мастерингу и проверке;
- `scripts/` — воспроизводимые локальные инструменты синтеза и сборки.

Репозиторий не содержит моделей, книг или сгенерированных аудиофайлов.
