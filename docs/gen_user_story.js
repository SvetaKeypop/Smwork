const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, HeadingLevel,
  LevelFormat, PageOrientation
} = require('docx');

const FONT = 'Times New Roman';
const SIZE = 28; // half-points -> 14pt
const SIZE_TITLE = 32; // 16pt
const SIZE_H2 = 28; // 14pt bold

const border = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
const cellBorders = { top: border, bottom: border, left: border, right: border };

// label column header style
function labelCell(text, width) {
  return new TableCell({
    borders: cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: 'D9D9D9', type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text, bold: true, font: FONT, size: SIZE })]
    })]
  });
}

function valueCell(runs, width) {
  return new TableCell({
    borders: cellBorders,
    width: { size: width, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: runs })]
  });
}

function mkRuns(parts) {
  // parts: array of { text, bold? }
  return parts.map(p => new TextRun({
    text: p.text,
    bold: !!p.bold,
    font: FONT,
    size: SIZE
  }));
}

// Builds one User Story card (4 rows: Заголовок / Заказчик / Примечание / Цель)
function buildCard(card) {
  const LABEL_W = 2200;
  const SUB_W = 1400;     // for "Как / Я хочу / Чтобы"
  const VAL_W = 5760;     // remaining
  // total = 2200 + 1400 + 5760 = 9360

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [LABEL_W, SUB_W, VAL_W],
    rows: [
      // row 1: Заголовок (spans last 2 cols)
      new TableRow({
        children: [
          labelCell('Заголовок', LABEL_W),
          new TableCell({
            borders: cellBorders,
            width: { size: SUB_W + VAL_W, type: WidthType.DXA },
            columnSpan: 2,
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({
              children: [new TextRun({ text: card.title, bold: true, font: FONT, size: SIZE })]
            })]
          })
        ]
      }),
      // row 2: Заказчик (actor) | Как | <actor>
      new TableRow({
        children: [
          labelCell('Заказчик (actor)', LABEL_W),
          labelCell('Как', SUB_W),
          valueCell(mkRuns([{ text: card.actor }]), VAL_W)
        ]
      }),
      // row 3: Примечание | Я хочу | <note>
      new TableRow({
        children: [
          labelCell('Примечание', LABEL_W),
          labelCell('Я хочу', SUB_W),
          valueCell(mkRuns([{ text: card.note }]), VAL_W)
        ]
      }),
      // row 4: Цель | Чтобы | <goal>
      new TableRow({
        children: [
          labelCell('Цель', LABEL_W),
          labelCell('Чтобы', SUB_W),
          valueCell(mkRuns([{ text: card.goal }]), VAL_W)
        ]
      })
    ]
  });
}

const cards = [
  {
    title: 'US-01. Регистрация',
    actor: 'новый пользователь',
    note: 'зарегистрироваться в системе по email и паролю',
    goal: 'получить доступ к функциям сайта (публикация рецептов, лайки, избранное)'
  },
  {
    title: 'US-02. Авторизация',
    actor: 'зарегистрированный пользователь',
    note: 'войти в систему по своим учётным данным',
    goal: 'получить доступ к личному кабинету и сохранённым данным'
  },
  {
    title: 'US-03. Просмотр каталога рецептов',
    actor: 'любой посетитель сайта',
    note: 'видеть список всех опубликованных рецептов на главной странице',
    goal: 'выбрать интересный рецепт для приготовления'
  },
  {
    title: 'US-04. Просмотр карточки рецепта',
    actor: 'любой посетитель сайта',
    note: 'открывать подробную страницу рецепта с фотографией, ингредиентами и шагами приготовления',
    goal: 'приготовить блюдо по понятной пошаговой инструкции'
  },
  {
    title: 'US-05. Публикация рецепта',
    actor: 'авторизованный пользователь',
    note: 'добавлять собственный рецепт (название, описание, фото, список ингредиентов, шаги)',
    goal: 'делиться кулинарным опытом с другими посетителями сайта'
  },
  {
    title: 'US-06. Лайк рецепта',
    actor: 'авторизованный пользователь',
    note: 'ставить и снимать лайк понравившемуся рецепту',
    goal: 'выражать одобрение и помогать другим находить лучшие рецепты'
  },
  {
    title: 'US-07. Добавление в избранное',
    actor: 'авторизованный пользователь',
    note: 'добавлять рецепты в избранное и просматривать их в отдельном разделе',
    goal: 'быстро возвращаться к понравившимся рецептам'
  },
  {
    title: 'US-08. Модерация контента',
    actor: 'администратор',
    note: 'удалять некорректные рецепты и блокировать пользователей-нарушителей',
    goal: 'поддерживать качество контента и порядок на сайте'
  }
];

// title block
function titleP(text, size = SIZE_TITLE, align = AlignmentType.CENTER) {
  return new Paragraph({
    alignment: align,
    spacing: { before: 120, after: 120 },
    children: [new TextRun({ text, bold: true, font: FONT, size })]
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, bold: !!opts.bold, font: FONT, size: SIZE })]
  });
}

function h2(text) {
  return new Paragraph({
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, font: FONT, size: SIZE_H2 })]
  });
}

// Build infoTable: 2 columns key/value
function infoTable(rows) {
  const KW = 3000, VW = 6360;
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [KW, VW],
    rows: rows.map(([k, v]) => new TableRow({
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: KW, type: WidthType.DXA },
          shading: { fill: 'F2F2F2', type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({
            children: [new TextRun({ text: k, bold: true, font: FONT, size: SIZE })]
          })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: VW, type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({
            children: [new TextRun({ text: v, font: FONT, size: SIZE })]
          })]
        })
      ]
    }))
  });
}

const children = [];

// Title
children.push(titleP('МИНОБРНАУКИ РОССИИ', 24));
children.push(p('Федеральное государственное бюджетное образовательное учреждение высшего образования', { align: AlignmentType.CENTER }));
children.push(p('«МИРЭА — Российский технологический университет»', { align: AlignmentType.CENTER, bold: true }));
children.push(p('Институт информационных технологий', { align: AlignmentType.CENTER }));
children.push(new Paragraph({ children: [new TextRun('')] }));
children.push(new Paragraph({ children: [new TextRun('')] }));
children.push(titleP('Итоговый проект по дисциплине'));
children.push(titleP('«Технологии разработки программных приложений»'));
children.push(titleP('Часть 1. Тема проекта, состав команды и функциональные требования', 28));
children.push(new Paragraph({ children: [new TextRun('')] }));

// Info block
children.push(h2('1. Общие сведения о проекте'));
children.push(infoTable([
  ['Тема проекта', 'Веб-приложение «Кулинарный блог / каталог рецептов»'],
  ['Направление', 'WEB-разработка'],
  ['Группа', 'ИКБО-12-24'],
  ['Состав команды', 'Лапин Матвей Максимович, Василенко Фёдор'],
  ['Целевая платформа', 'Linux-сервер (развёртывание), кроссбраузерный веб-интерфейс'],
  ['Бэкенд', 'Python 3.11+, FastAPI, SQLAlchemy, Uvicorn'],
  ['Фронтенд', 'HTML5, CSS3, JavaScript (без фреймворков)'],
  ['База данных', 'PostgreSQL 15+'],
  ['Система контроля версий', 'Git, удалённый репозиторий на GitHub']
]));

// Краткое описание
children.push(h2('2. Краткое описание проекта'));
children.push(p('Кулинарный блог — веб-приложение, позволяющее пользователям публиковать собственные рецепты, просматривать рецепты других участников сообщества, сохранять понравившиеся в избранное и оценивать их с помощью лайков. Гости сайта имеют возможность просматривать каталог и открывать карточки рецептов без регистрации. Для доступа к функциям публикации, лайков и избранного требуется регистрация и авторизация. Администратор обеспечивает модерацию контента: удаляет некорректные рецепты и блокирует пользователей-нарушителей.'));

// Роли
children.push(h2('3. Роли пользователей системы'));
children.push(p('• Гость — неавторизованный посетитель. Может просматривать каталог рецептов и открывать карточки.'));
children.push(p('• Пользователь — авторизованный посетитель. Может публиковать собственные рецепты, ставить лайки, добавлять в избранное.'));
children.push(p('• Администратор — управляет содержимым: удаляет рецепты, блокирует пользователей-нарушителей.'));

// User Stories
children.push(h2('4. Функциональные требования (User Story)'));
children.push(p('Функциональные требования к проекту сформулированы в виде пользовательских историй (User Story) согласно структуре:'));
children.push(p('«Как <роль/персонаж>, я хочу <действие>, чтобы <цель>».', { bold: true }));
children.push(p('Истории оформлены в виде карточек.'));
children.push(new Paragraph({ children: [new TextRun('')] }));

cards.forEach((c, idx) => {
  children.push(buildCard(c));
  if (idx !== cards.length - 1) {
    children.push(new Paragraph({ children: [new TextRun('')] }));
  }
});

children.push(new Paragraph({ children: [new TextRun('')] }));
children.push(p('Примечание: требования могут уточняться и дополняться в процессе работы над проектом.'));

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: SIZE } } }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4
        margin: { top: 1134, right: 850, bottom: 1134, left: 1701 } // 2/3/2/1.5 cm
      }
    },
    children
  }]
});

const out = path.join(__dirname, 'User_Story_Лапин_Василенко.docx');
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(out, buf);
  console.log('OK ->', out);
});
