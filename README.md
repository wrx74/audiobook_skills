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
