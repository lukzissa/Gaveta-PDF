# Gaveta PDF

<img width="400" height="400" alt="logo gaveta pdf" src="https://github.com/user-attachments/assets/65a05fc8-7c30-4de4-b3b5-b4cfaf8bd141" />
<img width="640" height="410" alt="screen gaveta pdf" src="https://github.com/user-attachments/assets/7b5787b6-0ba9-4fbd-b05b-7e0fde5a3694" />


Ferramentas de PDF **gratuitas, sem cadastro e 100% offline** para Windows.
Nenhum arquivo sai do seu computador, o que é ideal para documentos sigilosos, contratos
e processos de órgãos públicos.

Interface em **português (Brasil), inglês, espanhol e russo**: o idioma do Windows é usado
na primeira vez e pode ser trocado na barra lateral (o programa reinicia na hora).

## Download

Baixe a versão mais recente em **[Releases](../../releases/latest)**:

- **`GavetaPDF-X.Y-portatil.zip`**: extraia e abra o `GavetaPDF.exe`. Não precisa instalar e não
  deixa rastros no computador (tudo fica dentro da pasta do programa).
- **`GavetaPDF-X.Y-setup.exe`**: instalador, com atalhos e a opção “Enviar para” no Explorer.

O programa avisa sozinho quando sai uma versão nova e se atualiza com um clique.

## O que faz

| Ferramenta | Descrição |
|---|---|
| **Juntar PDFs** | Une vários PDFs e imagens num único arquivo, na ordem que você escolher |
| **Dividir e extrair** | Um arquivo por página, a cada N páginas, por intervalos (`1-3, 4-10, 11-`) ou extrair só algumas páginas |
| **Organizar páginas** | Miniaturas para arrastar e reordenar, girar, excluir e combinar páginas de vários arquivos |
| **Assinar PDF** | Desenhe, digite ou importe a foto da sua assinatura (o fundo branco é removido), clique para posicionar, arraste e redimensione; dá para repetir em todas as páginas (rubrica) |
| **Comprimir** | Três níveis (leve, recomendada, forte), opção de tons de cinza, processa vários arquivos de uma vez |
| **Converter** | PDF → Word (.docx editável, com tabelas e imagens), PDF → Excel (tabelas viram planilha; “R$ 1.234,56” vira número), PDF → PNG/JPG (96 a 600 DPI), imagens → PDF (A4 ou tamanho original), PDF → texto |
| **OCR** | Torna PDFs escaneados e fotos pesquisáveis (português, inglês, espanhol e russo) sem instalar o Tesseract |

Também dá para arrastar arquivos em qualquer tela, abrir PDFs pelo menu **Enviar para** do Explorer
e passar arquivos pela linha de comando.

## Rodar a partir do código

Requisito: [Python 3.10+](https://www.python.org/downloads/) (marque *Add python.exe to PATH*).

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python GavetaPDF.py
```

Os idiomas do OCR ficam na pasta `tessdata` (português, inglês, espanhol e russo já vêm incluídos).
Para adicionar outro idioma, baixe o `.traineddata` em
[tessdata_fast](https://github.com/tesseract-ocr/tessdata_fast) e coloque nessa pasta.

## Gerar o executável e o instalador

1. Dê dois cliques em **`build.bat`**. Ele cria o ambiente, instala as dependências, baixa os idiomas
   do OCR, roda os testes e gera `dist\GavetaPDF\GavetaPDF.exe`.
2. Instale o [Inno Setup 6](https://jrsoftware.org/isinfo.php) (gratuito), abra o **`installer.iss`** e
   clique em *Compile*. O instalador sai em `dist\GavetaPDF-1.0-setup.exe`.

### Versão portátil

O `build.bat` também gera `dist\GavetaPDF-1.0-portatil.zip`. Basta extrair e abrir o `GavetaPDF.exe`,
sem instalar. O programa **não grava nada fora da própria pasta**: nada no registro, `%APPDATA%` ou `%TEMP%`.

```
GavetaPDF.exe
GavetaPDF.ini          configurações (última pasta, assinatura salva…)
dados\gavetapdf.log    registro de erros
dados\ui\             imagens da interface
```

Para zerar tudo, apague o `GavetaPDF.ini` e a pasta `dados`. Se a pasta não aceitar gravação
(pendrive protegido), o programa funciona, só não lembra as configurações.
O instalador usa a pasta do usuário (`%LOCALAPPDATA%\Programs\Gaveta PDF`), sem pedir administrador,
para que o programa consiga gravar ao lado do `.exe`.

O build usa o modo "pasta" do PyInstaller, e não o "arquivo único", porque assim o programa
abre mais rápido e os antivírus acusam menos falsos positivos.

## Atualização automática

Ao abrir, o programa consulta a última release do repositório definido em `GITHUB_REPO`
(`gavetapdf/__init__.py`). Se houver versão nova, mostra as novidades e o botão **Atualizar agora**:
baixa o `.zip` portátil, confere o SHA-256 publicado pelo GitHub, fecha, troca os arquivos e abre
de novo. O `GavetaPDF.ini` e a pasta `dados` (configurações, assinatura salva, log) são mantidos.
Essa consulta é o único acesso à internet que o programa faz sozinho, e nenhum arquivo do usuário
é enviado. Sem internet, nada acontece. Rodando pelo código (`python GavetaPDF.py`) a verificação
fica desligada.

**Para publicar uma versão nova:**

1. Aumente `__version__` em `gavetapdf/__init__.py`, sempre com 2 números (`1.0` → `1.1` → … → `2.0`).
   É o único lugar: o `.exe`, o instalador e o `.zip` usam esse número.
2. Rode o `build.bat`: ele gera `dist\GavetaPDF-X.Y-portatil.zip`.
3. No GitHub, crie uma *release* com a tag `vX.Y`, escreva as novidades na descrição (elas
   aparecem na janela de atualização) e anexe o `GavetaPDF-X.Y-portatil.zip`
   (e o instalador, se quiser). O nome do anexo precisa terminar em `portatil.zip`.

## Traduções

Os textos são escritos em português no código, dentro de `tr("...")`, e traduzidos em
`gavetapdf/translations.py`. Ao criar um texto novo, acrescente a tradução lá: o teste
`tests/test_i18n.py` falha se faltar alguma ou se os marcadores `{0}`, `{1}` não baterem.

## Testes

```bat
python -m pytest tests
```

## Estrutura

```
GavetaPDF.py              ponto de entrada
gavetapdf/core/           processamento (sem interface, testável)
  organize.py            juntar, dividir, extrair, montar a partir de páginas
  compress.py            compressão
  convert.py             PDF ↔ imagem, PDF → texto, Word e Excel
  ocr.py                 OCR com o Tesseract embutido no MuPDF
  sign.py                assinatura visual (imagem) e limpeza do fundo da foto
gavetapdf/i18n.py         idioma da interface e função tr()
gavetapdf/translations.py traduções (inglês, espanhol, russo)
gavetapdf/ui/             interface (PySide6)
  main_window.py         janela, barra lateral, barra de progresso
  pages.py               telas de cada ferramenta
  organizer.py           editor de miniaturas
  signer.py              tela de assinatura (criar e posicionar)
  widgets.py, theme.py   componentes e visual
tests/                   testes do núcleo
tessdata/                idiomas do OCR
```

## Licença

Gaveta PDF © Lucas Issa, distribuído sob a **GNU AGPL-3.0** (veja o arquivo [`LICENSE`](LICENSE)).

Usa o **PyMuPDF** (AGPL-3.0), **Qt / PySide6** (LGPL-3.0), **pdf2docx** e **openpyxl** (MIT) e os
modelos de idioma do **Tesseract** (Apache-2.0). Por causa do PyMuPDF, uma versão de código fechado
exigiria a licença comercial da Artifex.

## Próximos passos (ideias)

- Assinatura digital com certificado A1/A3 (ICP-Brasil) e marca d'água
- Proteger e remover senha
- Numerar páginas e carimbos
- Publicar no **winget** (`winget install GavetaPDF`)
