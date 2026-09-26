"""Traduções da interface: frase em português → (inglês, espanhol, russo).

Os marcadores {0}, {1}… são preenchidos pelo programa e podem mudar de posição na frase.
Ao criar um texto novo com tr(), acrescente a tradução aqui (o teste
tests/test_i18n.py avisa quando falta alguma).
"""

TRANSLATIONS: dict[str, tuple[str, str, str]] = {
    # ------------------------------------------------------------------ geral / janela
    "Juntar PDFs": ("Merge PDFs", "Unir PDF", "Объединить PDF"),
    "Dividir e extrair": ("Split and extract", "Dividir y extraer", "Разделить и извлечь"),
    "Organizar páginas": ("Organize pages", "Organizar páginas", "Упорядочить страницы"),
    "Assinar PDF": ("Sign PDF", "Firmar PDF", "Подписать PDF"),
    "Comprimir": ("Compress", "Comprimir", "Сжать"),
    "Converter": ("Convert", "Convertir", "Конвертировать"),
    "OCR (pesquisável)": ("OCR (searchable)", "OCR (con búsqueda)", "OCR (поиск по тексту)"),
    "Abre a página de doação do PayPal no navegador": (
        "Opens the PayPal donation page in your browser",
        "Abre la página de donación de PayPal en el navegador",
        "Открывает страницу пожертвования PayPal в браузере"),
    "Pronto. Seus arquivos nunca saem do seu computador.": (
        "Ready. Your files never leave your computer.",
        "Listo. Tus archivos nunca salen de tu computadora.",
        "Готово. Ваши файлы никогда не покидают компьютер."),
    "Cancelar": ("Cancel", "Cancelar", "Отмена"),
    "Abrir arquivo": ("Open file", "Abrir archivo", "Открыть файл"),
    "Abrir pasta": ("Open folder", "Abrir carpeta", "Открыть папку"),
    "Ferramentas de PDF grátis\ne 100% offline": (
        "Free PDF tools,\n100% offline",
        "Herramientas PDF gratis\ny 100% sin conexión",
        "Бесплатные инструменты PDF,\n100% офлайн"),
    "Sobre o {0}": ("About {0}", "Acerca de {0}", "О программе {0}"),
    "v{0} · Desenvolvido por {1}": ("v{0} · Developed by {1}", "v{0} · Desarrollado por {1}", "v{0} · Разработчик: {1}"),
    "Versão {0}": ("Version {0}", "Versión {0}", "Версия {0}"),
    "O {0} é grátis e sem anúncios. Se ele te ajudou, considere uma doação.": (
        "{0} is free and ad-free. If it helped you, please consider a donation.",
        "{0} es gratis y sin anuncios. Si te ayudó, considera hacer una donación.",
        "{0} бесплатный и без рекламы. Если он вам помог, поддержите проект пожертвованием."),
    "Doar com": ("Donate with", "Donar con", "Пожертвовать через"),
    "Idioma": ("Language", "Idioma", "Язык"),
    "Não foi possível concluir a tarefa.": (
        "The task could not be completed.",
        "No se pudo completar la tarea.",
        "Не удалось выполнить задачу."),
    "Tarefa cancelada. Arquivos parciais podem ter sido criados.": (
        "Task cancelled. Partial files may have been created.",
        "Tarea cancelada. Es posible que se hayan creado archivos parciales.",
        "Задача отменена. Могли остаться частично созданные файлы."),
    "Ferramentas de PDF gratuitas que funcionam 100% offline.<br>Nenhum arquivo é enviado para a internet.<br><br>"
    "Desenvolvido por <b>{0}</b>.<br><br>Feito com PyMuPDF, Tesseract OCR e Qt (PySide6).<br>"
    "Distribuído sob a licença AGPL-3.0.": (
        "Free PDF tools that work 100% offline.<br>No file is ever sent to the internet.<br><br>"
        "Developed by <b>{0}</b>.<br><br>Built with PyMuPDF, Tesseract OCR and Qt (PySide6).<br>"
        "Distributed under the AGPL-3.0 license.",
        "Herramientas PDF gratuitas que funcionan 100% sin conexión.<br>Ningún archivo se envía a internet.<br><br>"
        "Desarrollado por <b>{0}</b>.<br><br>Hecho con PyMuPDF, Tesseract OCR y Qt (PySide6).<br>"
        "Distribuido bajo la licencia AGPL-3.0.",
        "Бесплатные инструменты PDF, работающие полностью офлайн.<br>Ни один файл не отправляется в интернет.<br><br>"
        "Разработчик: <b>{0}</b>.<br><br>Создано с помощью PyMuPDF, Tesseract OCR и Qt (PySide6).<br>"
        "Распространяется по лицензии AGPL-3.0."),
    "Aguarde a tarefa atual terminar.": (
        "Please wait for the current task to finish.",
        "Espera a que termine la tarea actual.",
        "Дождитесь завершения текущей задачи."),
    "Cancelando…": ("Cancelling…", "Cancelando…", "Отмена…"),
    "Modo claro": ("Light mode", "Modo claro", "Светлая тема"),
    "Modo escuro": ("Dark mode", "Modo oscuro", "Тёмная тема"),
    "Há uma tarefa em andamento. Deseja cancelar e sair?": (
        "A task is in progress. Do you want to cancel it and exit?",
        "Hay una tarea en curso. ¿Deseas cancelarla y salir?",
        "Выполняется задача. Отменить её и выйти?"),
    "Concluído, mas houve um problema ao exibir o resultado: {0}": (
        "Done, but there was a problem showing the result: {0}",
        "Listo, pero hubo un problema al mostrar el resultado: {0}",
        "Готово, но не удалось показать результат: {0}"),
    "Ocorreu um erro inesperado:\n{0}": (
        "An unexpected error occurred:\n{0}",
        "Ocurrió un error inesperado:\n{0}",
        "Произошла непредвиденная ошибка:\n{0}"),
    "Executar": ("Run", "Ejecutar", "Выполнить"),

    # ------------------------------------------------------------------ componentes comuns
    "Arquivos PDF (*.pdf)": ("PDF files (*.pdf)", "Archivos PDF (*.pdf)", "Файлы PDF (*.pdf)"),
    "Imagens (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)": (
        "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)",
        "Imágenes (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)",
        "Изображения (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)"),
    "PDFs e imagens (*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)": (
        "PDFs and images (*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)",
        "PDF e imágenes (*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)",
        "PDF и изображения (*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)"),
    "Arraste arquivos PDF para cá\nou clique em “Adicionar”": (
        "Drag PDF files here\nor click “Add”",
        "Arrastra archivos PDF aquí\no haz clic en “Añadir”",
        "Перетащите PDF-файлы сюда\nили нажмите «Добавить»"),
    "Escolher arquivo": ("Choose file", "Elegir archivo", "Выбрать файл"),
    "Adicionar": ("Add", "Añadir", "Добавить"),
    "Remover": ("Remove", "Quitar", "Убрать"),
    "Mover para cima": ("Move up", "Subir", "Вверх"),
    "Mover para baixo": ("Move down", "Bajar", "Вниз"),
    "Limpar": ("Clear", "Limpiar", "Очистить"),
    "Adicionar arquivos": ("Add files", "Añadir archivos", "Добавить файлы"),
    "{0} arquivo(s)": ("{0} file(s)", "{0} archivo(s)", "Файлов: {0}"),
    "Na mesma pasta do arquivo original": (
        "In the same folder as the original",
        "En la misma carpeta que el original",
        "В той же папке, что и оригинал"),
    "Em outra pasta:": ("In another folder:", "En otra carpeta:", "В другой папке:"),
    "Escolha uma pasta…": ("Choose a folder…", "Elige una carpeta…", "Выберите папку…"),
    "Salvar em…": ("Save to…", "Guardar en…", "Сохранить в…"),
    "Salvar": ("Save", "Guardar", "Сохранение"),
    "Salvar PDF": ("Save PDF", "Guardar PDF", "Сохранить PDF"),
    "Arraste PDFs para cá": ("Drag PDFs here", "Arrastra PDF aquí", "Перетащите PDF сюда"),
    "Arraste um PDF para cá": ("Drag a PDF here", "Arrastra un PDF aquí", "Перетащите PDF сюда"),
    "Adicione ao menos um PDF.": ("Add at least one PDF.", "Añade al menos un PDF.", "Добавьте хотя бы один PDF."),
    "Adicione ao menos um arquivo.": ("Add at least one file.", "Añade al menos un archivo.", "Добавьте хотя бы один файл."),
    "Adicione ao menos uma imagem.": ("Add at least one image.", "Añade al menos una imagen.", "Добавьте хотя бы одно изображение."),
    "Escolha a pasta onde os arquivos serão salvos.": (
        "Choose the folder where the files will be saved.",
        "Elige la carpeta donde se guardarán los archivos.",
        "Выберите папку для сохранения файлов."),
    "Escolha um nome diferente do arquivo original.": (
        "Choose a name different from the original file.",
        "Elige un nombre distinto al del archivo original.",
        "Выберите имя, отличное от исходного файла."),
    "Escolha um nome diferente dos arquivos de origem.": (
        "Choose a name different from the source files.",
        "Elige un nombre distinto al de los archivos de origen.",
        "Выберите имя, отличное от исходных файлов."),
    "Escolha um arquivo PDF.": ("Choose a PDF file.", "Elige un archivo PDF.", "Выберите PDF-файл."),

    # ------------------------------------------------------------------ progresso (núcleo)
    "Abrindo arquivo…": ("Opening file…", "Abriendo archivo…", "Открытие файла…"),
    "Concluído": ("Done", "Listo", "Готово"),
    "Recomprimindo imagens…": ("Recompressing images…", "Recomprimiendo imágenes…", "Пересжатие изображений…"),
    "Otimizando fontes…": ("Optimizing fonts…", "Optimizando fuentes…", "Оптимизация шрифтов…"),
    "Salvando…": ("Saving…", "Guardando…", "Сохранение…"),
    "Salvando PDF…": ("Saving PDF…", "Guardando PDF…", "Сохранение PDF…"),
    "Adicionando {0}": ("Adding {0}", "Añadiendo {0}", "Добавление: {0}"),
    "Página {0}": ("Page {0}", "Página {0}", "Страница {0}"),
    "Página {0} de {1}": ("Page {0} of {1}", "Página {0} de {1}", "Страница {0} из {1}"),
    "Criando parte {0} de {1}": ("Creating part {0} of {1}", "Creando parte {0} de {1}", "Создание части {0} из {1}"),
    "Extraindo páginas…": ("Extracting pages…", "Extrayendo páginas…", "Извлечение страниц…"),
    "Analisando o documento…": ("Analyzing the document…", "Analizando el documento…", "Анализ документа…"),
    "Criando o documento Word…": ("Creating the Word document…", "Creando el documento Word…", "Создание документа Word…"),
    "Tabelas": ("Tables", "Tablas", "Таблицы"),
    "Criando a planilha…": ("Creating the spreadsheet…", "Creando la hoja de cálculo…", "Создание таблицы…"),
    "Procurando tabelas na página {0}": (
        "Looking for tables on page {0}", "Buscando tablas en la página {0}", "Поиск таблиц на странице {0}"),
    "Procurando tabelas sem bordas na página {0}": (
        "Looking for borderless tables on page {0}",
        "Buscando tablas sin bordes en la página {0}",
        "Поиск таблиц без рамок на странице {0}"),
    "Reconhecendo texto — página {0} de {1}": (
        "Recognizing text — page {0} of {1}",
        "Reconociendo texto — página {0} de {1}",
        "Распознавание текста — страница {0} из {1}"),
    "Assinando página {0}": ("Signing page {0}", "Firmando página {0}", "Подписание страницы {0}"),

    # ------------------------------------------------------------------ erros (núcleo)
    "Arquivo não encontrado:\n{0}": ("File not found:\n{0}", "Archivo no encontrado:\n{0}", "Файл не найден:\n{0}"),
    "Não foi possível abrir o arquivo:\n{0}\n\n{1}": (
        "Could not open the file:\n{0}\n\n{1}",
        "No se pudo abrir el archivo:\n{0}\n\n{1}",
        "Не удалось открыть файл:\n{0}\n\n{1}"),
    "O arquivo “{0}” está protegido por senha.\nRemova a senha antes de usar este arquivo.": (
        "The file “{0}” is password protected.\nRemove the password before using this file.",
        "El archivo “{0}” está protegido con contraseña.\nQuita la contraseña antes de usar este archivo.",
        "Файл «{0}» защищён паролем.\nСнимите пароль, прежде чем использовать этот файл."),
    "Informe ao menos uma página ou intervalo (ex.: 1-3, 5, 8-).": (
        "Enter at least one page or range (e.g. 1-3, 5, 8-).",
        "Indica al menos una página o intervalo (ej.: 1-3, 5, 8-).",
        "Укажите хотя бы одну страницу или диапазон (напр.: 1-3, 5, 8-)."),
    "Intervalo inválido: “{0}”. Use o formato 1-3, 5, 8-.": (
        "Invalid range: “{0}”. Use the format 1-3, 5, 8-.",
        "Intervalo no válido: “{0}”. Usa el formato 1-3, 5, 8-.",
        "Неверный диапазон: «{0}». Используйте формат 1-3, 5, 8-."),
    "O intervalo “{0}” está fora do documento, que tem {1} página(s).": (
        "The range “{0}” is outside the document, which has {1} page(s).",
        "El intervalo “{0}” está fuera del documento, que tiene {1} página(s).",
        "Диапазон «{0}» выходит за пределы документа (страниц: {1})."),
    "Formato de imagem não suportado.": (
        "Unsupported image format.", "Formato de imagen no compatible.", "Неподдерживаемый формат изображения."),
    "Não foi possível ler a imagem:\n{0}": (
        "Could not read the image:\n{0}", "No se pudo leer la imagen:\n{0}", "Не удалось прочитать изображение:\n{0}"),
    "Este PDF não tem texto selecionável (parece ser escaneado ou uma foto).\n\n"
    "Passe o arquivo pelo OCR antes e depois converta o resultado.": (
        "This PDF has no selectable text (it seems to be a scan or a photo).\n\n"
        "Run the file through OCR first and then convert the result.",
        "Este PDF no tiene texto seleccionable (parece escaneado o una foto).\n\n"
        "Pasa el archivo por el OCR primero y luego convierte el resultado.",
        "В этом PDF нет выделяемого текста (похоже на скан или фото).\n\n"
        "Сначала обработайте файл через OCR, затем конвертируйте результат."),
    "Nenhuma tabela foi encontrada em “{0}”.\n\nPara levar só o texto, use PDF → Word ou PDF → Texto.": (
        "No tables were found in “{0}”.\n\nTo get just the text, use PDF → Word or PDF → Text.",
        "No se encontraron tablas en “{0}”.\n\nPara obtener solo el texto, usa PDF → Word o PDF → Texto.",
        "В «{0}» не найдено таблиц.\n\nЧтобы получить только текст, используйте PDF → Word или PDF → Текст."),
    "Não foi possível salvar “{0}”.\nSe ele estiver aberto no Excel, feche e tente de novo.": (
        "Could not save “{0}”.\nIf it is open in Excel, close it and try again.",
        "No se pudo guardar “{0}”.\nSi está abierto en Excel, ciérralo e inténtalo de nuevo.",
        "Не удалось сохранить «{0}».\nЕсли файл открыт в Excel, закройте его и повторите попытку."),
    "Não foi possível salvar “{0}”.\nSe ele estiver aberto no Word, feche e tente de novo.": (
        "Could not save “{0}”.\nIf it is open in Word, close it and try again.",
        "No se pudo guardar “{0}”.\nSi está abierto en Word, ciérralo e inténtalo de nuevo.",
        "Не удалось сохранить «{0}».\nЕсли файл открыт в Word, закройте его и повторите попытку."),
    "Não foi possível converter “{0}” para Word.\n\n{1}": (
        "Could not convert “{0}” to Word.\n\n{1}",
        "No se pudo convertir “{0}” a Word.\n\n{1}",
        "Не удалось конвертировать «{0}» в Word.\n\n{1}"),
    "O número de páginas por arquivo deve ser 1 ou mais.": (
        "The number of pages per file must be 1 or more.",
        "El número de páginas por archivo debe ser 1 o más.",
        "Количество страниц в файле должно быть не меньше 1."),
    "Não há páginas para salvar.": ("There are no pages to save.", "No hay páginas para guardar.", "Нет страниц для сохранения."),
    "Os arquivos de idioma do OCR não foram encontrados.\n"
    "Coloque os arquivos .traineddata na pasta “tessdata” ao lado do programa.": (
        "The OCR language files were not found.\n"
        "Put the .traineddata files in the “tessdata” folder next to the program.",
        "No se encontraron los archivos de idioma del OCR.\n"
        "Coloca los archivos .traineddata en la carpeta “tessdata” junto al programa.",
        "Файлы языков OCR не найдены.\n"
        "Поместите файлы .traineddata в папку «tessdata» рядом с программой."),
    "Idioma de OCR não instalado: {0}": (
        "OCR language not installed: {0}", "Idioma de OCR no instalado: {0}", "Язык OCR не установлен: {0}"),
    "Falha no OCR da página {0}:\n{1}": (
        "OCR failed on page {0}:\n{1}", "Error de OCR en la página {0}:\n{1}", "Ошибка OCR на странице {0}:\n{1}"),
    "A imagem parece estar em branco: nenhum traço de assinatura foi encontrado.": (
        "The image seems to be blank: no signature strokes were found.",
        "La imagen parece estar en blanco: no se encontró ningún trazo de firma.",
        "Изображение выглядит пустым: подпись не найдена."),
    "Clique na página para posicionar a assinatura antes de salvar.": (
        "Click on the page to place the signature before saving.",
        "Haz clic en la página para colocar la firma antes de guardar.",
        "Щёлкните по странице, чтобы разместить подпись перед сохранением."),
    "Não foi possível abrir a imagem da assinatura.\n\n{0}": (
        "Could not open the signature image.\n\n{0}",
        "No se pudo abrir la imagen de la firma.\n\n{0}",
        "Не удалось открыть изображение подписи.\n\n{0}"),
    "A página {0} não existe neste documento.": (
        "Page {0} does not exist in this document.",
        "La página {0} no existe en este documento.",
        "Страницы {0} нет в этом документе."),

    # ------------------------------------------------------------------ nomes de arquivos gerados
    "{0} - página {1}.{2}": ("{0} - page {1}.{2}", "{0} - página {1}.{2}", "{0} - страница {1}.{2}"),
    "{0} - páginas {1}.pdf": ("{0} - pages {1}.pdf", "{0} - páginas {1}.pdf", "{0} - страницы {1}.pdf"),
    "===== Página {0} =====\n{1}": ("===== Page {0} =====\n{1}", "===== Página {0} =====\n{1}", "===== Страница {0} =====\n{1}"),
    "{0} (organizado).pdf": ("{0} (organized).pdf", "{0} (organizado).pdf", "{0} (упорядочено).pdf"),
    "{0} (unido).pdf": ("{0} (merged).pdf", "{0} (unido).pdf", "{0} (объединено).pdf"),
    "{0} (extraído).pdf": ("{0} (extracted).pdf", "{0} (extraído).pdf", "{0} (извлечено).pdf"),
    "{0} (comprimido).pdf": ("{0} (compressed).pdf", "{0} (comprimido).pdf", "{0} (сжато).pdf"),
    "{0} (pesquisável).pdf": ("{0} (searchable).pdf", "{0} (con búsqueda).pdf", "{0} (с поиском).pdf"),
    "{0} (assinado).pdf": ("{0} (signed).pdf", "{0} (firmado).pdf", "{0} (подписано).pdf"),
    "{0} - imagens": ("{0} - images", "{0} - imágenes", "{0} - изображения"),

    # ------------------------------------------------------------------ Juntar
    "Una vários PDFs (e imagens) em um único arquivo. Arraste para mudar a ordem.": (
        "Combine several PDFs (and images) into a single file. Drag to change the order.",
        "Une varios PDF (e imágenes) en un solo archivo. Arrastra para cambiar el orden.",
        "Объедините несколько PDF (и изображений) в один файл. Перетаскивайте, чтобы изменить порядок."),
    "Arraste PDFs ou imagens para cá\na ordem da lista é a ordem do arquivo final": (
        "Drag PDFs or images here\nthe list order is the order of the final file",
        "Arrastra PDF o imágenes aquí\nel orden de la lista es el orden del archivo final",
        "Перетащите PDF или изображения сюда\nпорядок в списке — порядок в итоговом файле"),
    "Dica: para escolher páginas específicas de cada arquivo, use “Organizar páginas”.": (
        "Tip: to pick specific pages from each file, use “Organize pages”.",
        "Consejo: para elegir páginas concretas de cada archivo, usa “Organizar páginas”.",
        "Совет: чтобы выбрать отдельные страницы из каждого файла, используйте «Упорядочить страницы»."),
    "Adicione pelo menos dois arquivos para juntar.": (
        "Add at least two files to merge.", "Añade al menos dos archivos para unir.", "Добавьте хотя бы два файла для объединения."),
    "Salvar PDF unido": ("Save merged PDF", "Guardar PDF unido", "Сохранить объединённый PDF"),
    "{0} arquivos unidos em “{1}”.": ("{0} files merged into “{1}”.", "{0} archivos unidos en “{1}”.", "Файлов объединено: {0} → «{1}»."),
    "Juntando arquivos…": ("Merging files…", "Uniendo archivos…", "Объединение файлов…"),

    # ------------------------------------------------------------------ Dividir
    "Separe um PDF em vários arquivos ou tire dele só as páginas que interessam.": (
        "Split a PDF into several files or take out only the pages you need.",
        "Separa un PDF en varios archivos o saca solo las páginas que te interesan.",
        "Разделите PDF на несколько файлов или извлеките только нужные страницы."),
    "Dividir PDF": ("Split PDF", "Dividir PDF", "Разделить PDF"),
    "Um arquivo para cada página": ("One file per page", "Un archivo por página", "Отдельный файл для каждой страницы"),
    "Um arquivo a cada": ("One file every", "Un archivo cada", "Новый файл каждые"),
    "páginas": ("pages", "páginas", "стр."),
    "Um arquivo para cada intervalo:": ("One file per range:", "Un archivo por intervalo:", "Отдельный файл для каждого диапазона:"),
    "ex.: 1-3, 4-10, 11-": ("e.g. 1-3, 4-10, 11-", "ej.: 1-3, 4-10, 11-", "напр.: 1-3, 4-10, 11-"),
    "Extrair páginas para um só arquivo:": ("Extract pages into a single file:", "Extraer páginas a un solo archivo:", "Извлечь страницы в один файл:"),
    "ex.: 1, 3, 5-7": ("e.g. 1, 3, 5-7", "ej.: 1, 3, 5-7", "напр.: 1, 3, 5-7"),
    "Arquivo": ("File", "Archivo", "Файл"),
    "Como dividir": ("How to split", "Cómo dividir", "Способ разделения"),
    "Intervalos: separe por vírgula. “8-” vai da página 8 até o fim.": (
        "Ranges: separate with commas. “8-” goes from page 8 to the end.",
        "Intervalos: sepáralos con comas. “8-” va de la página 8 hasta el final.",
        "Диапазоны разделяйте запятыми. «8-» — со страницы 8 до конца."),
    "{0} página(s)": ("{0} page(s)", "{0} página(s)", "Страниц: {0}"),
    "Salvar páginas extraídas": ("Save extracted pages", "Guardar páginas extraídas", "Сохранить извлечённые страницы"),
    "Páginas extraídas para “{0}”.": ("Pages extracted to “{0}”.", "Páginas extraídas en “{0}”.", "Страницы извлечены в «{0}»."),
    "Escolha a pasta para salvar as partes": (
        "Choose the folder to save the parts", "Elige la carpeta para guardar las partes", "Выберите папку для сохранения частей"),
    "PDF dividido em {0} arquivo(s).": ("PDF split into {0} file(s).", "PDF dividido en {0} archivo(s).", "PDF разделён, файлов: {0}."),
    "Dividindo…": ("Splitting…", "Dividiendo…", "Разделение…"),

    # ------------------------------------------------------------------ Organizar
    "Monte um novo PDF escolhendo páginas de um ou vários arquivos. Arraste para reordenar; "
    "selecione várias com Ctrl ou Shift.": (
        "Build a new PDF by choosing pages from one or more files. Drag to reorder; "
        "select several with Ctrl or Shift.",
        "Crea un nuevo PDF eligiendo páginas de uno o varios archivos. Arrastra para reordenar; "
        "selecciona varias con Ctrl o Shift.",
        "Соберите новый PDF из страниц одного или нескольких файлов. Перетаскивайте для изменения порядка; "
        "выделяйте несколько с Ctrl или Shift."),
    "Arraste PDFs ou imagens para cá\n\nDepois arraste as miniaturas para mudar a ordem,\n"
    "use os botões para girar ou excluir páginas.": (
        "Drag PDFs or images here\n\nThen drag the thumbnails to change the order,\n"
        "use the buttons to rotate or delete pages.",
        "Arrastra PDF o imágenes aquí\n\nLuego arrastra las miniaturas para cambiar el orden,\n"
        "usa los botones para girar o eliminar páginas.",
        "Перетащите PDF или изображения сюда\n\nЗатем перетаскивайте миниатюры, чтобы изменить порядок,\n"
        "кнопками можно поворачивать и удалять страницы."),
    "Adicionar PDF": ("Add PDF", "Añadir PDF", "Добавить PDF"),
    "Adicionar PDFs ou imagens": ("Add PDFs or images", "Añadir PDF o imágenes", "Добавить PDF или изображения"),
    "Girar para a esquerda (Ctrl+L)": ("Rotate left (Ctrl+L)", "Girar a la izquierda (Ctrl+L)", "Повернуть влево (Ctrl+L)"),
    "Girar para a direita (Ctrl+R)": ("Rotate right (Ctrl+R)", "Girar a la derecha (Ctrl+R)", "Повернуть вправо (Ctrl+R)"),
    "Excluir": ("Delete", "Eliminar", "Удалить"),
    "Excluir páginas selecionadas (Delete)": (
        "Delete selected pages (Delete)", "Eliminar las páginas seleccionadas (Supr)", "Удалить выбранные страницы (Delete)"),
    "Limpar tudo": ("Clear all", "Limpiar todo", "Очистить всё"),
    "Remover todas as páginas": ("Remove all pages", "Quitar todas las páginas", "Убрать все страницы"),
    "Tamanho das miniaturas": ("Thumbnail size", "Tamaño de las miniaturas", "Размер миниатюр"),
    "Zoom": ("Zoom", "Zoom", "Масштаб"),
    "{0} — página {1}": ("{0} — page {1}", "{0} — página {1}", "{0} — страница {1}"),
    "{0} p.{1}": ("{0} p.{1}", "{0} p.{1}", "{0} стр.{1}"),
    "Adicione páginas antes de salvar.": ("Add pages before saving.", "Añade páginas antes de guardar.", "Добавьте страницы перед сохранением."),
    "Salvar PDF organizado": ("Save organized PDF", "Guardar PDF organizado", "Сохранить упорядоченный PDF"),
    "PDF salvo com {0} página(s).": ("PDF saved with {0} page(s).", "PDF guardado con {0} página(s).", "PDF сохранён, страниц: {0}."),

    # ------------------------------------------------------------------ Comprimir
    "Comprimir PDF": ("Compress PDF", "Comprimir PDF", "Сжать PDF"),
    "Diminua o tamanho dos arquivos para enviar por e-mail, WhatsApp ou sistemas com limite de upload.": (
        "Reduce file size to send by email, WhatsApp or systems with upload limits.",
        "Reduce el tamaño de los archivos para enviarlos por correo, WhatsApp o sistemas con límite de subida.",
        "Уменьшите размер файлов для отправки по почте, в WhatsApp или в системы с ограничением загрузки."),
    "Leve": ("Light", "Ligera", "Слабое"),
    "Qualidade quase igual, redução menor": (
        "Nearly identical quality, smaller reduction", "Calidad casi igual, menor reducción", "Качество почти без изменений, меньшее сжатие"),
    "Recomendada": ("Recommended", "Recomendada", "Рекомендуемое"),
    "Bom equilíbrio para enviar por e-mail": (
        "Good balance for sending by email", "Buen equilibrio para enviar por correo", "Хороший баланс для отправки по почте"),
    "Forte": ("Strong", "Fuerte", "Сильное"),
    "Menor tamanho possível, imagens mais simples": (
        "Smallest possible size, simpler images", "El menor tamaño posible, imágenes más simples", "Минимальный размер, упрощённые изображения"),
    "Arraste um ou vários PDFs para cá": ("Drag one or more PDFs here", "Arrastra uno o varios PDF aquí", "Перетащите один или несколько PDF сюда"),
    "Imagens em tons de cinza (reduz mais)": (
        "Grayscale images (smaller files)", "Imágenes en escala de grises (reduce más)", "Изображения в оттенках серого (сильнее сжатие)"),
    "Nível de compressão": ("Compression level", "Nivel de compresión", "Степень сжатия"),
    "O original nunca é alterado. O novo arquivo recebe “(comprimido)” no nome.": (
        "The original is never changed. The new file gets “(compressed)” in its name.",
        "El original nunca se modifica. El nuevo archivo lleva “(comprimido)” en el nombre.",
        "Оригинал не изменяется. К имени нового файла добавляется «(сжато)»."),
    "Este PDF já estava otimizado; não foi possível reduzir mais.": (
        "This PDF was already optimized; it could not be reduced further.",
        "Este PDF ya estaba optimizado; no se pudo reducir más.",
        "Этот PDF уже оптимизирован; уменьшить его сильнее не удалось."),
    "{0} arquivos comprimidos: {1}": ("{0} files compressed: {1}", "{0} archivos comprimidos: {1}", "Сжато файлов: {0}: {1}"),
    "Arquivo comprimido: {0}": ("File compressed: {0}", "Archivo comprimido: {0}", "Файл сжат: {0}"),
    "Comprimindo…": ("Compressing…", "Comprimiendo…", "Сжатие…"),

    # ------------------------------------------------------------------ Converter
    "Transforme PDF em Word, Excel, imagens ou texto, e fotos ou digitalizações em PDF.": (
        "Turn PDFs into Word, Excel, images or text, and photos or scans into PDF.",
        "Convierte PDF en Word, Excel, imágenes o texto, y fotos o escaneos en PDF.",
        "Превращайте PDF в Word, Excel, изображения или текст, а фото и сканы — в PDF."),
    "PDF → Word": ("PDF → Word", "PDF → Word", "PDF → Word"),
    "Converter para Word": ("Convert to Word", "Convertir a Word", "Конвертировать в Word"),
    "PDF → Excel": ("PDF → Excel", "PDF → Excel", "PDF → Excel"),
    "Converter para Excel": ("Convert to Excel", "Convertir a Excel", "Конвертировать в Excel"),
    "PDF → Imagem": ("PDF → Image", "PDF → Imagen", "PDF → Изображение"),
    "Converter em imagens": ("Convert to images", "Convertir en imágenes", "Конвертировать в изображения"),
    "Imagem → PDF": ("Image → PDF", "Imagen → PDF", "Изображение → PDF"),
    "Criar PDF": ("Create PDF", "Crear PDF", "Создать PDF"),
    "PDF → Texto": ("PDF → Text", "PDF → Texto", "PDF → Текст"),
    "Extrair texto": ("Extract text", "Extraer texto", "Извлечь текст"),
    "Cria um arquivo .docx editável, mantendo parágrafos, tabelas e imagens.": (
        "Creates an editable .docx file, keeping paragraphs, tables and images.",
        "Crea un archivo .docx editable, manteniendo párrafos, tablas e imágenes.",
        "Создаёт редактируемый файл .docx с сохранением абзацев, таблиц и изображений."),
    "Funciona melhor com PDFs gerados no computador. Documentos escaneados precisam passar pelo OCR antes.": (
        "Works best with PDFs created on a computer. Scanned documents need OCR first.",
        "Funciona mejor con PDF creados en la computadora. Los documentos escaneados necesitan pasar por el OCR antes.",
        "Лучше всего работает с PDF, созданными на компьютере. Сканы сначала нужно обработать через OCR."),
    "Layouts muito elaborados podem precisar de pequenos ajustes no Word.": (
        "Very complex layouts may need small adjustments in Word.",
        "Los diseños muy elaborados pueden necesitar pequeños ajustes en Word.",
        "Сложные макеты могут потребовать небольшой доработки в Word."),
    "Arraste PDFs com tabelas para cá": ("Drag PDFs with tables here", "Arrastra PDF con tablas aquí", "Перетащите PDF с таблицами сюда"),
    "Organização": ("Layout", "Organización", "Размещение"),
    "Uma aba para cada página": ("One sheet per page", "Una hoja por página", "Отдельный лист для каждой страницы"),
    "Todas as tabelas em uma aba": ("All tables in one sheet", "Todas las tablas en una hoja", "Все таблицы на одном листе"),
    "Transformar números em valores do Excel": (
        "Turn numbers into Excel values", "Convertir los números en valores de Excel", "Превращать числа в значения Excel"),
    "“R$ 1.234,56”, “12,5” e “15%” viram números, prontos para somar e fazer contas.": (
        "“$1,234.56”, “12.5” and “15%” become numbers, ready for sums and formulas.",
        "“1.234,56 €”, “12,5” y “15%” se convierten en números, listos para sumar y calcular.",
        "«1 234,56 ₽», «12,5» и «15%» становятся числами, готовыми для сумм и формул."),
    "Encontra as tabelas do PDF (extratos, relatórios, notas) e cria um arquivo .xlsx. "
    "Códigos com zero à esquerda, CPF e datas continuam como texto.": (
        "Finds the tables in the PDF (statements, reports, invoices) and creates an .xlsx file. "
        "Codes with leading zeros, ID numbers and dates stay as text.",
        "Encuentra las tablas del PDF (extractos, informes, facturas) y crea un archivo .xlsx. "
        "Los códigos con ceros a la izquierda, números de identificación y fechas se mantienen como texto.",
        "Находит таблицы в PDF (выписки, отчёты, счета) и создаёт файл .xlsx. "
        "Коды с ведущими нулями, номера документов и даты остаются текстом."),
    "PNG (sem perda, ideal para texto)": ("PNG (lossless, best for text)", "PNG (sin pérdida, ideal para texto)", "PNG (без потерь, для текста)"),
    "JPG (menor, ideal para fotos)": ("JPG (smaller, best for photos)", "JPG (más ligero, ideal para fotos)", "JPG (меньше, для фотографий)"),
    "Baixa — 96 DPI (tela)": ("Low — 96 DPI (screen)", "Baja — 96 DPI (pantalla)", "Низкое — 96 DPI (экран)"),
    "Média — 150 DPI": ("Medium — 150 DPI", "Media — 150 DPI", "Среднее — 150 DPI"),
    "Alta — 300 DPI (impressão)": ("High — 300 DPI (print)", "Alta — 300 DPI (impresión)", "Высокое — 300 DPI (печать)"),
    "Máxima — 600 DPI": ("Maximum — 600 DPI", "Máxima — 600 DPI", "Максимальное — 600 DPI"),
    "Todas as páginas (ou ex.: 1-3, 7)": ("All pages (or e.g. 1-3, 7)", "Todas las páginas (o ej.: 1-3, 7)", "Все страницы (или напр.: 1-3, 7)"),
    "Formato": ("Format", "Formato", "Формат"),
    "Qualidade": ("Quality", "Calidad", "Качество"),
    "Páginas": ("Pages", "Páginas", "Страницы"),
    "Cada PDF gera uma pasta com uma imagem por página.": (
        "Each PDF creates a folder with one image per page.",
        "Cada PDF genera una carpeta con una imagen por página.",
        "Для каждого PDF создаётся папка с изображением каждой страницы."),
    "Arraste imagens (JPG, PNG, TIFF…) para cá\ncada imagem vira uma página": (
        "Drag images (JPG, PNG, TIFF…) here\neach image becomes a page",
        "Arrastra imágenes (JPG, PNG, TIFF…) aquí\ncada imagen se convierte en una página",
        "Перетащите изображения (JPG, PNG, TIFF…) сюда\nкаждое станет страницей"),
    "A4 (ajusta a imagem na folha)": ("A4 (fits the image on the page)", "A4 (ajusta la imagen a la hoja)", "A4 (вписать изображение в лист)"),
    "Tamanho original da imagem": ("Original image size", "Tamaño original de la imagen", "Исходный размер изображения"),
    "Sem margem": ("No margin", "Sin margen", "Без полей"),
    "Pequena (5 mm)": ("Small (5 mm)", "Pequeño (5 mm)", "Узкие (5 мм)"),
    "Normal (10 mm)": ("Normal (10 mm)", "Normal (10 mm)", "Обычные (10 мм)"),
    "Grande (20 mm)": ("Large (20 mm)", "Grande (20 mm)", "Широкие (20 мм)"),
    "Tamanho da página": ("Page size", "Tamaño de página", "Размер страницы"),
    "Margem": ("Margin", "Margen", "Поля"),
    "Dica: depois de criar o PDF, use o OCR para tornar o texto pesquisável.": (
        "Tip: after creating the PDF, use OCR to make the text searchable.",
        "Consejo: después de crear el PDF, usa el OCR para que el texto se pueda buscar.",
        "Совет: после создания PDF используйте OCR, чтобы по тексту можно было искать."),
    "Gera um arquivo .txt com o texto de cada página. PDFs escaneados precisam passar pelo OCR antes.": (
        "Creates a .txt file with the text of each page. Scanned PDFs need OCR first.",
        "Genera un archivo .txt con el texto de cada página. Los PDF escaneados necesitan pasar por el OCR antes.",
        "Создаёт файл .txt с текстом каждой страницы. Сканы сначала нужно обработать через OCR."),
    "Escolha a pasta onde os documentos serão salvos.": (
        "Choose the folder where the documents will be saved.",
        "Elige la carpeta donde se guardarán los documentos.",
        "Выберите папку для сохранения документов."),
    "Escolha a pasta onde as planilhas serão salvas.": (
        "Choose the folder where the spreadsheets will be saved.",
        "Elige la carpeta donde se guardarán las hojas de cálculo.",
        "Выберите папку для сохранения таблиц."),
    "Escolha a pasta onde os textos serão salvos.": (
        "Choose the folder where the text files will be saved.",
        "Elige la carpeta donde se guardarán los textos.",
        "Выберите папку для сохранения текстов."),
    "Escolha a pasta onde as imagens serão salvas.": (
        "Choose the folder where the images will be saved.",
        "Elige la carpeta donde se guardarán las imágenes.",
        "Выберите папку для сохранения изображений."),
    "{0} arquivo(s) convertido(s) para Word.": (
        "{0} file(s) converted to Word.", "{0} archivo(s) convertido(s) a Word.", "Конвертировано в Word файлов: {0}."),
    "Convertendo para Word…": ("Converting to Word…", "Convirtiendo a Word…", "Конвертация в Word…"),
    "{0} tabela(s) exportada(s) para {1} planilha(s).": (
        "{0} table(s) exported to {1} spreadsheet(s).",
        "{0} tabla(s) exportada(s) a {1} hoja(s) de cálculo.",
        "Экспортировано таблиц: {0}, файлов Excel: {1}."),
    "Convertendo para Excel…": ("Converting to Excel…", "Convirtiendo a Excel…", "Конвертация в Excel…"),
    "{0} imagem(ns) criada(s).": ("{0} image(s) created.", "{0} imagen(es) creada(s).", "Создано изображений: {0}."),
    "Convertendo…": ("Converting…", "Convirtiendo…", "Конвертация…"),
    "PDF criado com {0} imagem(ns).": ("PDF created with {0} image(s).", "PDF creado con {0} imagen(es).", "PDF создан, изображений: {0}."),
    "Criando PDF…": ("Creating PDF…", "Creando PDF…", "Создание PDF…"),
    "Texto extraído de {0} arquivo(s).": ("Text extracted from {0} file(s).", "Texto extraído de {0} archivo(s).", "Текст извлечён, файлов: {0}."),
    "Extraindo texto…": ("Extracting text…", "Extrayendo texto…", "Извлечение текста…"),

    # ------------------------------------------------------------------ OCR
    "OCR — tornar pesquisável": ("OCR — make searchable", "OCR — hacer que se pueda buscar", "OCR — сделать доступным для поиска"),
    "Reconhece o texto de PDFs escaneados e fotos de documentos. Depois você pode buscar (Ctrl+F), "
    "selecionar e copiar o texto. Tudo acontece no seu computador.": (
        "Recognizes the text in scanned PDFs and photos of documents. Then you can search (Ctrl+F), "
        "select and copy the text. Everything happens on your computer.",
        "Reconoce el texto de PDF escaneados y fotos de documentos. Después podrás buscar (Ctrl+F), "
        "seleccionar y copiar el texto. Todo ocurre en tu computadora.",
        "Распознаёт текст в отсканированных PDF и фотографиях документов. Затем текст можно искать (Ctrl+F), "
        "выделять и копировать. Всё происходит на вашем компьютере."),
    "Reconhecer texto": ("Recognize text", "Reconocer texto", "Распознать текст"),
    "Arraste PDFs escaneados ou fotos de documentos para cá": (
        "Drag scanned PDFs or photos of documents here",
        "Arrastra PDF escaneados o fotos de documentos aquí",
        "Перетащите отсканированные PDF или фото документов сюда"),
    "Nenhum idioma instalado. Coloque arquivos .traineddata na pasta “tessdata”.": (
        "No language installed. Put .traineddata files in the “tessdata” folder.",
        "Ningún idioma instalado. Coloca archivos .traineddata en la carpeta “tessdata”.",
        "Языки не установлены. Поместите файлы .traineddata в папку «tessdata»."),
    "Rápido (200 DPI)": ("Fast (200 DPI)", "Rápido (200 DPI)", "Быстро (200 DPI)"),
    "Recomendado (300 DPI)": ("Recommended (300 DPI)", "Recomendado (300 DPI)", "Рекомендуется (300 DPI)"),
    "Máxima precisão (400 DPI)": ("Maximum accuracy (400 DPI)", "Máxima precisión (400 DPI)", "Максимальная точность (400 DPI)"),
    "Pular páginas que já têm texto": ("Skip pages that already have text", "Omitir páginas que ya tienen texto", "Пропускать страницы, где уже есть текст"),
    "Idioma do documento": ("Document language", "Idioma del documento", "Язык документа"),
    "O novo arquivo recebe “(pesquisável)” no nome. Para reduzir o tamanho depois, use Comprimir.": (
        "The new file gets “(searchable)” in its name. To reduce its size afterwards, use Compress.",
        "El nuevo archivo lleva “(con búsqueda)” en el nombre. Para reducir su tamaño después, usa Comprimir.",
        "К имени нового файла добавляется «(с поиском)». Чтобы потом уменьшить размер, используйте «Сжать»."),
    "Marque ao menos um idioma.": ("Select at least one language.", "Marca al menos un idioma.", "Отметьте хотя бы один язык."),
    "Texto reconhecido em {0} página(s).": (
        "Text recognized on {0} page(s).", "Texto reconocido en {0} página(s).", "Текст распознан, страниц: {0}."),
    "{0} já tinham texto e foram mantidas.": (
        "{0} already had text and were kept.", "{0} ya tenían texto y se mantuvieron.", "Уже с текстом и оставлены без изменений: {0}."),
    "Reconhecendo texto…": ("Recognizing text…", "Reconociendo texto…", "Распознавание текста…"),
    "Português": ("Portuguese", "Portugués", "Португальский"),
    "Inglês": ("English", "Inglés", "Английский"),
    "Espanhol": ("Spanish", "Español", "Испанский"),
    "Russo": ("Russian", "Ruso", "Русский"),
    "Francês": ("French", "Francés", "Французский"),
    "Alemão": ("German", "Alemán", "Немецкий"),
    "Italiano": ("Italian", "Italiano", "Итальянский"),

    # ------------------------------------------------------------------ Assinar
    "Crie sua assinatura e clique no documento onde ela deve aparecer. "
    "Arraste para mover e use o canto para mudar o tamanho.": (
        "Create your signature and click on the document where it should appear. "
        "Drag to move it and use the corner to resize.",
        "Crea tu firma y haz clic en el documento donde debe aparecer. "
        "Arrastra para moverla y usa la esquina para cambiar el tamaño.",
        "Создайте подпись и щёлкните в документе там, где она должна появиться. "
        "Перетаскивайте её и тяните за угол, чтобы изменить размер."),
    "Salvar PDF assinado": ("Save signed PDF", "Guardar PDF firmado", "Сохранить подписанный PDF"),
    "Abrir PDF": ("Open PDF", "Abrir PDF", "Открыть PDF"),
    "Página anterior (Page Up)": ("Previous page (Page Up)", "Página anterior (Re Pág)", "Предыдущая страница (Page Up)"),
    "Próxima página (Page Down)": ("Next page (Page Down)", "Página siguiente (Av Pág)", "Следующая страница (Page Down)"),
    "de {0}": ("of {0}", "de {0}", "из {0}"),
    "Sua assinatura": ("Your signature", "Tu firma", "Ваша подпись"),
    "Nenhuma assinatura criada": ("No signature created", "Ninguna firma creada", "Подпись ещё не создана"),
    "Criar assinatura": ("Create signature", "Crear firma", "Создать подпись"),
    "Trocar assinatura": ("Change signature", "Cambiar firma", "Изменить подпись"),
    "Posicionar": ("Placement", "Colocar", "Размещение"),
    "Clique na página para colocar a assinatura. Selecione e aperte Delete para remover.": (
        "Click on the page to place the signature. Select it and press Delete to remove it.",
        "Haz clic en la página para colocar la firma. Selecciónala y pulsa Supr para quitarla.",
        "Щёлкните по странице, чтобы поставить подпись. Выделите её и нажмите Delete, чтобы убрать."),
    "Repetir em todas as páginas": ("Repeat on all pages", "Repetir en todas las páginas", "Повторить на всех страницах"),
    "Coloca a assinatura selecionada na mesma posição em todas as páginas (útil para rubricar)": (
        "Places the selected signature in the same position on every page (useful for initials)",
        "Coloca la firma seleccionada en la misma posición en todas las páginas (útil para rubricar)",
        "Ставит выбранную подпись в то же место на каждой странице (удобно для визирования)"),
    "Remover selecionada": ("Remove selected", "Quitar la seleccionada", "Убрать выбранную"),
    "Remover a assinatura selecionada (Delete)": (
        "Remove the selected signature (Delete)", "Quitar la firma seleccionada (Supr)", "Убрать выбранную подпись (Delete)"),
    "Remover todas": ("Remove all", "Quitar todas", "Убрать все"),
    "Esta é uma assinatura visual (imagem). Ela não substitui a assinatura digital com certificado "
    "(ICP-Brasil ou gov.br) quando esta for exigida.": (
        "This is a visual signature (image). It does not replace a certificate-based digital signature "
        "when one is required.",
        "Esta es una firma visual (imagen). No sustituye a la firma digital con certificado "
        "cuando esta sea obligatoria.",
        "Это визуальная подпись (изображение). Она не заменяет электронную подпись с сертификатом, "
        "если такая требуется."),
    "Assinatura repetida em mais {0} página(s).": (
        "Signature repeated on {0} more page(s).", "Firma repetida en {0} página(s) más.", "Подпись добавлена ещё на страниц: {0}."),
    "{0} assinatura(s) em {1} página(s)": (
        "{0} signature(s) on {1} page(s)", "{0} firma(s) en {1} página(s)", "Подписей: {0}, страниц: {1}"),
    "Abra um PDF para assinar.": ("Open a PDF to sign.", "Abre un PDF para firmar.", "Откройте PDF для подписи."),
    "Crie sua assinatura antes de salvar.": (
        "Create your signature before saving.", "Crea tu firma antes de guardar.", "Создайте подпись перед сохранением."),
    "Clique na página para posicionar a assinatura.": (
        "Click on the page to place the signature.", "Haz clic en la página para colocar la firma.", "Щёлкните по странице, чтобы разместить подпись."),
    "Este PDF já tem uma assinatura digital. Qualquer alteração faz essa assinatura aparecer como inválida.\n\n"
    "Deseja continuar mesmo assim?": (
        "This PDF already has a digital signature. Any change will make that signature show as invalid.\n\n"
        "Do you want to continue anyway?",
        "Este PDF ya tiene una firma digital. Cualquier cambio hará que esa firma aparezca como no válida.\n\n"
        "¿Deseas continuar de todos modos?",
        "В этом PDF уже есть электронная подпись. Любое изменение сделает её недействительной.\n\n"
        "Всё равно продолжить?"),
    "PDF assinado ({0} assinatura(s)) salvo como “{1}”.": (
        "Signed PDF ({0} signature(s)) saved as “{1}”.",
        "PDF firmado ({0} firma(s)) guardado como “{1}”.",
        "Подписанный PDF (подписей: {0}) сохранён как «{1}»."),
    "Assinando…": ("Signing…", "Firmando…", "Подписание…"),
    "Arraste um PDF para cá\nou clique em “Abrir PDF”": (
        "Drag a PDF here\nor click “Open PDF”",
        "Arrastra un PDF aquí\no haz clic en “Abrir PDF”",
        "Перетащите PDF сюда\nили нажмите «Открыть PDF»"),
    "Azul": ("Blue", "Azul", "Синий"),
    "Preto": ("Black", "Negro", "Чёрный"),
    "Desenhar": ("Draw", "Dibujar", "Нарисовать"),
    "Digitar": ("Type", "Escribir", "Напечатать"),
    "Importar imagem": ("Import image", "Importar imagen", "Загрузить изображение"),
    "Lembrar esta assinatura neste computador": (
        "Remember this signature on this computer", "Recordar esta firma en esta computadora", "Запомнить подпись на этом компьютере"),
    "Fica salva só neste computador, para reutilizar na próxima vez.": (
        "It is saved only on this computer, to reuse next time.",
        "Se guarda solo en esta computadora, para reutilizarla la próxima vez.",
        "Сохраняется только на этом компьютере, чтобы использовать в следующий раз."),
    "Usar assinatura": ("Use signature", "Usar firma", "Использовать подпись"),
    "Cor da tinta:": ("Ink color:", "Color de la tinta:", "Цвет чернил:"),
    "Desfazer": ("Undo", "Deshacer", "Отменить"),
    "Assine aqui com o mouse, a caneta ou o dedo": (
        "Sign here with the mouse, pen or finger", "Firma aquí con el ratón, el lápiz o el dedo", "Распишитесь здесь мышью, пером или пальцем"),
    "Nome": ("Name", "Nombre", "Имя"),
    "Digite seu nome": ("Type your name", "Escribe tu nombre", "Введите своё имя"),
    "Estilo": ("Style", "Estilo", "Стиль"),
    "A prévia aparece aqui": ("The preview appears here", "La vista previa aparece aquí", "Здесь появится предпросмотр"),
    "Escolher imagem…": ("Choose image…", "Elegir imagen…", "Выбрать изображение…"),
    "Remover o fundo branco e recortar as bordas": (
        "Remove the white background and trim the edges", "Quitar el fondo blanco y recortar los bordes", "Убрать белый фон и обрезать края"),
    "Escolha uma foto ou digitalização da sua assinatura\n(de preferência em papel branco, com caneta escura)": (
        "Choose a photo or scan of your signature\n(preferably on white paper, with a dark pen)",
        "Elige una foto o escaneo de tu firma\n(preferiblemente en papel blanco, con bolígrafo oscuro)",
        "Выберите фото или скан подписи\n(лучше на белой бумаге, тёмной ручкой)"),
    "Imagem da assinatura": ("Signature image", "Imagen de la firma", "Изображение подписи"),
    "Não foi possível abrir a imagem.\n\n{0}": (
        "Could not open the image.\n\n{0}", "No se pudo abrir la imagen.\n\n{0}", "Не удалось открыть изображение.\n\n{0}"),

    # ------------------------------------------------------------------ atualização automática
    "Atualização disponível": ("Update available", "Actualización disponible", "Доступно обновление"),
    "<b>O {0} {1} está disponível.</b><br>Você está usando a versão {2}.": (
        "<b>{0} {1} is available.</b><br>You are using version {2}.",
        "<b>{0} {1} está disponible.</b><br>Estás usando la versión {2}.",
        "<b>Доступна версия {0} {1}.</b><br>У вас установлена версия {2}."),
    "Novidades:": ("What's new:", "Novedades:", "Что нового:"),
    "O programa vai baixar a versão nova, fechar e abrir de novo já atualizado. "
    "Suas configurações e a assinatura salva são mantidas.": (
        "The program will download the new version, close and reopen already updated. "
        "Your settings and saved signature are kept.",
        "El programa descargará la nueva versión, se cerrará y se abrirá de nuevo ya actualizado. "
        "Se conservan tus ajustes y la firma guardada.",
        "Программа скачает новую версию, закроется и откроется уже обновлённой. "
        "Настройки и сохранённая подпись останутся."),
    "Baixe a versão nova pela página de download.": (
        "Download the new version from the download page.",
        "Descarga la nueva versión desde la página de descarga.",
        "Скачайте новую версию со страницы загрузки."),
    "Atualizar agora": ("Update now", "Actualizar ahora", "Обновить сейчас"),
    "Abrir página de download": ("Open download page", "Abrir página de descarga", "Открыть страницу загрузки"),
    "Depois": ("Later", "Más tarde", "Позже"),
    "Baixando atualização…": ("Downloading update…", "Descargando actualización…", "Загрузка обновления…"),
    "Baixando atualização… {0:.1f} MB": (
        "Downloading update… {0:.1f} MB", "Descargando actualización… {0:.1f} MB", "Загрузка обновления… {0:.1f} МБ"),
    "Instalando a atualização…": ("Installing the update…", "Instalando la actualización…", "Установка обновления…"),
    "A pasta do programa não permite gravação, então não dá para atualizar automaticamente.\n"
    "Baixe a versão nova pelo site.": (
        "The program folder is read-only, so it cannot update automatically.\n"
        "Download the new version from the website.",
        "La carpeta del programa no permite escritura, así que no se puede actualizar automáticamente.\n"
        "Descarga la nueva versión desde el sitio.",
        "Папка программы доступна только для чтения, поэтому автообновление невозможно.\n"
        "Скачайте новую версию с сайта."),
    "A versão nova ainda não tem o arquivo para atualização automática.\nBaixe pelo site.": (
        "The new version does not have the automatic update file yet.\nDownload it from the website.",
        "La nueva versión todavía no tiene el archivo de actualización automática.\nDescárgala desde el sitio.",
        "Для новой версии ещё нет файла автообновления.\nСкачайте её с сайта."),
    "Não foi possível baixar a atualização.\nVerifique a internet e tente de novo.\n\n{0}": (
        "Could not download the update.\nCheck your internet connection and try again.\n\n{0}",
        "No se pudo descargar la actualización.\nRevisa tu conexión a internet e inténtalo de nuevo.\n\n{0}",
        "Не удалось скачать обновление.\nПроверьте подключение к интернету и повторите попытку.\n\n{0}"),
    "O arquivo baixado está corrompido (a verificação de segurança falhou).\nTente de novo mais tarde.": (
        "The downloaded file is corrupted (the security check failed).\nTry again later.",
        "El archivo descargado está dañado (la verificación de seguridad falló).\nInténtalo de nuevo más tarde.",
        "Скачанный файл повреждён (проверка безопасности не пройдена).\nПовторите попытку позже."),
    "O arquivo de atualização é inválido.": (
        "The update file is invalid.", "El archivo de actualización no es válido.", "Файл обновления повреждён."),
}
