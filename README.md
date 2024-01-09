# Проектное задание второго спринта

*Спроектировать и реализовать планировщик задач для выполнения поступающих задач.*

## Тому, кто будет это читать

- **Документация доступна онлайн:**
    - [**e-io.github.io/async-python-sprint-2**](https://e-io.github.io/async-python-sprint-2/how-to-guides/)


### Диаграмма
Взаимодействие компонентов изображено на [этой диаграмме](diagram.png).
![image](diagram.png)

### Документация

Документация по этому проекту доступна благодаря использованию документатора MkDocs.

- Документация доступна онлайн:
    - [e-io.github.io/async-python-sprint-2](https://e-io.github.io/async-python-sprint-2/how-to-guides/)

- Также можно посмотреть офлайн:
    - как сайт - откройте `site/index.html`
    - как отдельные файлы markdown - смотрите папку `docs/`
    

Также сайт может генерироваться "на лету" при помощи команды
```shell
mkdocs serve  
```

### Личные результаты достигнутые в ходе работы над этим проектом:
- Впервые в жизни я писал тесты на каком-либо специальном фреймворке (`pytest`). До этого я только использовал py-тесты написанные другими. 
- Впервые я применил документатор. Я давно думал о том, как генерить файлы с docstring'ами, но не находил как это сделать. 
- А тут нашёл `mkdocs` и сгерировал статический сайт-документацию на github pages. 

Теперь моя жизнь делится на 'до' и 'после'. Очень интересно мнение со стороны об этих двух пробах пера.

А также:

- Впервые использовал корутины. 
- Впервые сделал бэкапы процессов, способные восстановиться хоть после перезапуска компьютера. В частности, впервые использовал функцию pickle.

### Примечание
В текущем проекте я не успел реализовать опциональные параметры для классов Job и Schedule. 
Однако сделал все нужные заглушки, включая запись этих параметров в бэкап-файл и полное восстановление этих параметров при рестарте.

__________________

## Описание задания

**1. Описать реализацию класса `Scheduler`.**

Условия и требования:

- Планировщик одновременно может выполнять до 10 задач (дефолтное значение, может быть изменено).
- Возможность добавить задачу в планировщик и запустить её в рамках ограничений планировщика и настроек, указанных в задаче.
- При штатном завершении работы планировщик сохраняет статус выполняемых и ожидающих задач.
- После рестарта восстанавливается последнее состояние и задачи продолжают выполняться.

**2. Описать реализацию класса `Job`.**

Условия и требования:

- У задачи может быть указана длительность выполнения (опциональный параметр). Если параметр указан, то задача прекращает выполняться, если время выполнения превысило указанный параметр.
- У задачи может быть указано время запуска (опциональный параметр). Если параметр указан, то задача стартует в указанный временной период.
- У задачи может быть указан параметр количества рестартов (опциональный параметр). Если в ходе выполнения задачи произошёл сбой или задачи-зависимости не были выполнены, то задача будет перезапущена указанное количество раз. Если параметр не указан, то количество рестартов равно 0.
- У задачи может быть указаны зависимости — задача или задачи, от которых зависит её выполнение (опциональный параметр). Если параметр указан, то задача не может стартовать до момента, пока не будут завершены задачи-зависимости.


**3. Проверить работу планировщика на различных задачах.**

Условия и требования:

- работа с файловой системой: создание, удаление, изменение директорий и файлов;
- работа с файлами: создание, чтение, запись;
- работа с сетью: обработка ссылок (GET-запросы) и анализ полученного результата;
- описать конвейер выполнения основной задачи минимум из 3 задач, зависящих друг от друга и выполняющихся последовательно друг за другом.

## Требования к решению

1. Используйте корутины и генераторы, изученные в теоретической части.
2. Использование потоков и процессов не запрещено.
3. Использование `asyncio` запрещено.
4. Используйте встроенные библиотеки и модули языка.
5. Используйте концепции ООП.
6. Используйте аннотацию типов.
7. Логируйте результаты действий.
8. Предусмотрите обработку исключительных ситуаций.
9. Приведите стиль кода в соответствие pep8, flake8, mypy.

## Рекомендации к решению

1. Покройте написанный код тестами.
2. Для хранения статуса задач или планировщика используйте `.lock`-файлы и иные текстовые форматы — например, `txt` или `json`.
3. Организуйте структуру хранения задач и/или их зависимостей в рамках отдельных директорий с определенным наименованием, используя `uid` или кастомный шаблон. Использование ссылок (`symlink`) не запрещено.
4. Сигнатура описания классов может быть изменена под ваше усмотрение. Создавать дополнительные классы не запрещено.
5. Используйте примитивы синхронизации, например, [Timer](https://docs.python.org/3/library/threading.html#timer-objects) или [Condition](https://docs.python.org/3/library/threading.html#condition-objects).
6. По возможности, решение должно полностью строиться на использовании корутин.

Схематично сервис представлен на [диаграмме](schema.png).
![image](schema.png)