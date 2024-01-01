# О MkDocs

Эта документация построена при помощи документатора 

## Базовые команды

Чтобы запустить документацию в браузере используя IDE или терминал
```shell
mkdocs serve
```

Пересобрать статический сайт (хранится в папке site). 
Не требует обращения к терминалу каждый раз, но требует периодической пересборки.
```shell
mkdocs build
```

Обновить документацию на гитхабе (требуется чтобы обновлённые файлы уже были на гитхабе хоть на какой-то ветке).
```shell
mkdocs gh-deploy
```
## Задействованные файлы и папки под mkdocs

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
    site/
        ...       # Статический сайт

## Дополнительно о mkdocs

Краткая справочная информация по mkdocs
```shell
mkdocs -h
```

Полезная статья со внешнего источника о работе документатора mkdocs:
```shell
open https://realpython.com/python-project-documentation-with-mkdocs/
```

Больше информации - на официальном сайте
```shell
open https://www.mkdocs.org
```
