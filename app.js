const STORAGE_KEY = "rf-open-source-desk-v1";

const STAGE_RANK = {
  express: 1,
  standard: 2,
  deep: 3,
};

const CATEGORY_LABELS = {
  registration: "Регистрация",
  disclosure: "Раскрытие и банкротство",
  finance: "Финансы",
  litigation: "Суды",
  enforcement: "Исполнительные производства",
  procurement: "Закупки",
  supervision: "Надзор и проверки",
  licensing: "Лицензии и аккредитация",
  sanctions: "Санкции",
  digital: "Цифровой след",
  media: "Медиа",
};

const LANE_LABELS = {
  registry: "Регистрация и раскрытие",
  legal: "Суды и принудительное исполнение",
  market: "Рынок, закупки и лицензии",
  digital: "Цифровой и медийный след",
};

const FIELD_LABELS = {
  entityName: "наименование",
  inn: "ИНН",
  ogrn: "ОГРН",
  domain: "домен",
  orgPhone: "телефон",
  region: "регион",
  sector: "отрасль",
};

const SOURCE_LIBRARY = [
  {
    id: "egrul",
    name: "ЕГРЮЛ / ЕГРИП (ФНС)",
    category: "registration",
    lane: "registry",
    official: true,
    url: "https://egrul.nalog.ru/index.html",
    description:
      "Базовая регистрационная выписка: статус, дата регистрации, адрес, ОКВЭД, руководитель или ИП.",
    subjects: ["company", "ip"],
    minStage: "express",
    order: 10,
    fields: ["inn", "ogrn", "entityName"],
    outputs: ["статус", "адрес", "ОКВЭД"],
  },
  {
    id: "transparent-business",
    name: "Прозрачный бизнес (ФНС)",
    category: "disclosure",
    lane: "registry",
    official: true,
    url: "https://pb.nalog.ru/",
    description:
      "Публичные индикаторы ФНС: адрес массовой регистрации, связи, сведения о налоговой дисциплине и отчетности.",
    subjects: ["company", "ip"],
    minStage: "express",
    order: 20,
    fields: ["inn", "entityName"],
    outputs: ["массовость", "связанные лица", "налоговые индикаторы"],
  },
  {
    id: "accounting",
    name: "Бухгалтерская отчетность (ФНС)",
    category: "finance",
    lane: "registry",
    official: true,
    url: "https://bo.nalog.gov.ru/",
    description:
      "Публикуемая бухгалтерская отчетность и состав отчетных форм для юрлиц.",
    subjects: ["company"],
    minStage: "standard",
    order: 30,
    fields: ["inn", "entityName"],
    outputs: ["баланс", "финрезультат", "периодичность отчетности"],
  },
  {
    id: "fedresurs",
    name: "Федресурс",
    category: "disclosure",
    lane: "registry",
    official: true,
    url: "https://fedresurs.ru/",
    description:
      "Сообщения о банкротстве, ликвидации, реорганизации, залогах и других значимых событиях.",
    subjects: ["company", "ip"],
    minStage: "express",
    order: 40,
    fields: ["inn", "ogrn", "entityName"],
    outputs: ["банкротство", "реорганизация", "существенные уведомления"],
  },
  {
    id: "kad",
    name: "Картотека арбитражных дел",
    category: "litigation",
    lane: "legal",
    official: true,
    url: "https://kad.arbitr.ru/",
    description:
      "Арбитражные споры, роли истца или ответчика, динамика и предмет судебных дел.",
    subjects: ["company", "ip"],
    minStage: "express",
    order: 50,
    fields: ["entityName", "inn", "ogrn"],
    outputs: ["споры", "роль в деле", "частота исков"],
  },
  {
    id: "fssp",
    name: "ФССП - банк данных исполнительных производств",
    category: "enforcement",
    lane: "legal",
    official: true,
    url: "https://fssp.gov.ru/iss/ip",
    description:
      "Исполнительные производства по юридическим лицам и ИП. Для точности полезно дополнить поиск регионом.",
    subjects: ["company", "ip"],
    minStage: "standard",
    order: 60,
    fields: ["entityName", "region"],
    outputs: ["исполнительные производства", "территория", "статус"],
  },
  {
    id: "procurement",
    name: "ЕИС / Госзакупки",
    category: "procurement",
    lane: "market",
    official: true,
    url: "https://zakupki.gov.ru/epz/main/public/home.html",
    description:
      "История участия в закупках, контракты, жалобы, риск-факторы по госконтрактам и РНП.",
    subjects: ["company", "ip"],
    minStage: "standard",
    order: 70,
    fields: ["inn", "entityName"],
    outputs: ["контракты", "жалобы", "РНП"],
  },
  {
    id: "supervision",
    name: "Единый реестр проверок Генпрокуратуры",
    category: "supervision",
    lane: "market",
    official: true,
    url: "https://proverki.gov.ru/portal/public-search",
    description:
      "Публичные сведения о проверках, надзорных мероприятиях и их результатах.",
    subjects: ["company", "ip"],
    minStage: "standard",
    order: 80,
    fields: ["inn", "entityName"],
    outputs: ["проверки", "надзорный орган", "результат"],
  },
  {
    id: "rosakkreditatsiya",
    name: "Росаккредитация",
    category: "licensing",
    lane: "market",
    official: true,
    url: "https://pub.fsa.gov.ru/ral",
    description:
      "Аккредитация и статус организаций, работающих в регулируемых сегментах. Актуально для лицензируемой деятельности.",
    subjects: ["company", "ip"],
    minStage: "standard",
    order: 90,
    fields: ["inn", "entityName"],
    profiles: ["licensed", "finance"],
    outputs: ["аккредитация", "область действия", "статус"],
  },
  {
    id: "cbr",
    name: "Банк России - справочник участников финансового рынка",
    category: "licensing",
    lane: "market",
    official: true,
    url: "https://cbr.ru/finorg/foinfo/",
    description:
      "Реестры и статусы финансовых организаций, лицензий и специальных разрешений Банка России.",
    subjects: ["company"],
    minStage: "standard",
    order: 100,
    fields: ["entityName", "inn"],
    profiles: ["finance"],
    outputs: ["лицензия", "статус", "тип финорганизации"],
  },
  {
    id: "ofac",
    name: "OFAC Sanctions Search",
    category: "sanctions",
    lane: "market",
    official: true,
    url: "https://sanctionssearch.ofac.treas.gov/",
    description:
      "Официальный поиск по санкционным спискам OFAC. Для поиска часто нужна англоязычная транслитерация названия.",
    subjects: ["company", "ip"],
    minStage: "standard",
    order: 110,
    fields: ["entityName", "inn"],
    outputs: ["совпадения по санкционным спискам", "алиасы", "комментарии"],
  },
  {
    id: "whois",
    name: "WHOIS / RDAP",
    category: "digital",
    lane: "digital",
    official: false,
    url: "https://rdap.org/",
    description:
      "Дата регистрации домена, nameservers и базовые технические сигналы цифрового следа компании.",
    subjects: ["company", "ip"],
    minStage: "standard",
    order: 120,
    fields: ["domain"],
    requiresAny: ["domain"],
    outputs: ["дата регистрации", "регистратор", "технический профиль"],
  },
  {
    id: "media",
    name: "Поиск по новостям и отраслевым публикациям",
    category: "media",
    lane: "digital",
    official: false,
    url: "https://news.google.com/",
    description:
      "Нейтральный мониторинг публикаций, пресс-релизов и отраслевых упоминаний компании или ИП.",
    subjects: ["company", "ip"],
    minStage: "deep",
    order: 130,
    fields: ["entityName", "inn", "domain"],
    outputs: ["упоминания", "публичные инциденты", "репутационный контекст"],
  },
];

const RISK_ITEMS = [
  {
    id: "mass-address",
    category: "Регистрация",
    label: "Признаки массового адреса или номинального управления",
    note: "Проверьте совпадение адреса, фактическое присутствие, контактные данные и структуру управления.",
    weight: 25,
    action: "Запросить подтверждение адреса, структуру владения и фактическое присутствие компании.",
  },
  {
    id: "recent-registration",
    category: "Регистрация",
    label: "Недавняя регистрация или резкая смена реквизитов",
    note: "Молодая компания сама по себе не проблема, но требует допроверки деловой истории.",
    weight: 12,
    action: "Сверить историю изменений в ЕГРЮЛ и запросить подтверждение операционной деятельности.",
  },
  {
    id: "management-changes",
    category: "Корпоративные изменения",
    label: "Частая смена директора, адреса или ОКВЭД",
    note: "Резкая динамика регистрационных данных может требовать объяснения со стороны контрагента.",
    weight: 15,
    action: "Запросить пояснения по смене управления, адреса и бизнес-модели.",
  },
  {
    id: "no-statements",
    category: "Финансы",
    label: "Отчетность отсутствует, нерегулярна или выглядит неполной",
    note: "Проверьте, обязана ли компания публиковать отчетность и за какие периоды данные доступны.",
    weight: 15,
    action: "Запросить финансовые документы или пояснение по отсутствию публичной отчетности.",
  },
  {
    id: "fedresurs-events",
    category: "Банкротство и раскрытие",
    label: "Есть сообщения о банкротстве, ликвидации, реорганизации или существенных обременениях",
    note: "Это один из наиболее весомых red flags для контрагентской проверки.",
    weight: 35,
    action: "Остановить сделку до разъяснения статуса по Федресурсу и юридического заключения.",
  },
  {
    id: "arbitration-pattern",
    category: "Суды",
    label: "Повторяющиеся судебные споры, особенно в роли ответчика",
    note: "Смотрите не только наличие дел, но и частоту, суммы и предмет споров.",
    weight: 20,
    action: "Провести углубленный анализ ключевых споров и запросить позицию контрагента.",
  },
  {
    id: "enforcement-cases",
    category: "Исполнение",
    label: "Открытые исполнительные производства",
    note: "Обратите внимание на сумму и характер задолженности, а также повторяемость производств.",
    weight: 18,
    action: "Проверить сумму обязательств и запросить подтверждение урегулирования задолженности.",
  },
  {
    id: "procurement-issues",
    category: "Закупки",
    label: "Есть жалобы, расторгнутые контракты или попадание в РНП",
    note: "Проблемы в закупках могут указывать на операционные или комплаенс-риски.",
    weight: 22,
    action: "Сверить историю контрактов и выяснить причины жалоб, расторжений или включения в РНП.",
  },
  {
    id: "license-mismatch",
    category: "Лицензии",
    label: "Лицензия, аккредитация или отраслевой статус не подтверждаются",
    note: "Особенно важно для финансовых организаций и лицензируемых отраслей.",
    weight: 25,
    action: "Проверить профильный реестр лицензий и не заключать договор без подтверждения статуса.",
  },
  {
    id: "sanctions-hit",
    category: "Санкции",
    label: "Есть совпадения по санкционным или ограничительным спискам",
    note: "Требует отдельного юридического и санкционного анализа, включая совпадения по алиасам.",
    weight: 40,
    action: "Немедленно передать кейс на санкционную проверку и приостановить онбординг до решения.",
  },
  {
    id: "digital-mismatch",
    category: "Цифровой след",
    label: "Сайт и контакты не согласуются с регистрационными данными",
    note: "Обратите внимание на свежий домен, отсутствие делового контента и расхождения в реквизитах.",
    weight: 10,
    action: "Сверить домен, телефон, email и юридические реквизиты с источниками ФНС и сайтом.",
  },
  {
    id: "adverse-media",
    category: "Медиа",
    label: "Есть подтвержденные негативные публикации из надежных источников",
    note: "Не учитывайте анонимные или явно нерепутационные публикации без дополнительной верификации.",
    weight: 12,
    action: "Проверить первоисточник публикации и запросить комментарий по подтвержденным инцидентам.",
  },
];

const DEFAULT_STATE = {
  profile: {
    subjectType: "company",
    entityName: "",
    inn: "",
    ogrn: "",
    domain: "",
    orgPhone: "",
    region: "",
    sector: "",
    regulatoryProfile: "general",
    stage: "express",
  },
  completedSources: [],
  selectedRisks: [],
  notes: {
    caseGoal:
      "Проверка благонадежности нового контрагента перед заключением договора.",
    confirmedFacts: "",
    conclusion: "",
    nextSteps: "",
  },
};

const elements = {
  profileForm: document.querySelector("#profile-form"),
  workflowList: document.querySelector("#workflow-list"),
  briefingCard: document.querySelector("#briefing-card"),
  sourceGrid: document.querySelector("#source-grid"),
  sourceStats: document.querySelector("#source-stats"),
  sourceSearch: document.querySelector("#source-search"),
  categoryFilter: document.querySelector("#category-filter"),
  officialOnly: document.querySelector("#official-only"),
  riskList: document.querySelector("#risk-list"),
  riskScore: document.querySelector("#risk-score"),
  riskBadge: document.querySelector("#risk-badge"),
  riskLevel: document.querySelector("#risk-level"),
  riskExplainer: document.querySelector("#risk-explainer"),
  riskFlags: document.querySelector("#risk-flags"),
  riskActions: document.querySelector("#risk-actions"),
  dashboardBoard: document.querySelector("#dashboard-board"),
  metricRecommended: document.querySelector("#metric-recommended"),
  metricCompleted: document.querySelector("#metric-completed"),
  metricRisk: document.querySelector("#metric-risk"),
  caseGoal: document.querySelector("#case-goal"),
  confirmedFacts: document.querySelector("#confirmed-facts"),
  conclusion: document.querySelector("#conclusion"),
  nextSteps: document.querySelector("#next-steps"),
  copyBriefing: document.querySelector("#copy-briefing"),
  downloadBriefing: document.querySelector("#download-briefing"),
  copyReport: document.querySelector("#copy-report"),
  downloadJson: document.querySelector("#download-json"),
  resetState: document.querySelector("#reset-state"),
};

let state = loadState();

init();

function init() {
  hydrateForm();
  bindInputs();
  renderRiskChecklist();
  render();
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return cloneDefaultState();
    }

    const parsed = JSON.parse(raw);
    return {
      profile: { ...DEFAULT_STATE.profile, ...(parsed.profile || {}) },
      completedSources: Array.isArray(parsed.completedSources)
        ? parsed.completedSources
        : [],
      selectedRisks: Array.isArray(parsed.selectedRisks) ? parsed.selectedRisks : [],
      notes: { ...DEFAULT_STATE.notes, ...(parsed.notes || {}) },
    };
  } catch (error) {
    return cloneDefaultState();
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function hydrateForm() {
  const { profile, notes } = state;
  Object.entries(profile).forEach(([key, value]) => {
    const field = document.querySelector(`#${key}`);
    if (field) {
      field.value = value;
    }
  });

  elements.caseGoal.value = notes.caseGoal;
  elements.confirmedFacts.value = notes.confirmedFacts;
  elements.conclusion.value = notes.conclusion;
  elements.nextSteps.value = notes.nextSteps;
}

function bindInputs() {
  elements.profileForm.addEventListener("input", handleProfileInput);
  elements.profileForm.addEventListener("change", handleProfileInput);

  elements.sourceSearch.addEventListener("input", renderSourceLibrary);
  elements.categoryFilter.addEventListener("change", renderSourceLibrary);
  elements.officialOnly.addEventListener("change", renderSourceLibrary);

  elements.riskList.addEventListener("change", handleRiskToggle);
  elements.sourceGrid.addEventListener("click", handleSourceActions);
  elements.dashboardBoard.addEventListener("change", handleDashboardToggle);

  [elements.caseGoal, elements.confirmedFacts, elements.conclusion, elements.nextSteps].forEach(
    (field) => {
      field.addEventListener("input", () => {
        state.notes = {
          caseGoal: elements.caseGoal.value.trim(),
          confirmedFacts: elements.confirmedFacts.value.trim(),
          conclusion: elements.conclusion.value.trim(),
          nextSteps: elements.nextSteps.value.trim(),
        };
        saveState();
        renderBriefingCard();
      });
    },
  );

  elements.copyBriefing.addEventListener("click", async () => {
    await copyText(buildBriefingMarkdown());
    setTemporaryButtonLabel(elements.copyBriefing, "Скопировано");
  });

  elements.downloadBriefing.addEventListener("click", () => {
    downloadFile(`${buildFileStem()}-briefing.md`, buildBriefingMarkdown());
  });

  elements.copyReport.addEventListener("click", async () => {
    await copyText(buildFullReportMarkdown());
    setTemporaryButtonLabel(elements.copyReport, "Скопировано");
  });

  elements.downloadJson.addEventListener("click", () => {
    const payload = {
      generatedAt: new Date().toISOString(),
      profile: state.profile,
      completedSources: getCompletedSourceObjects().map((source) => source.name),
      recommendedSources: getRecommendedSources().map((source) => source.name),
      riskSummary: getRiskSummary(),
      notes: state.notes,
    };

    downloadFile(
      `${buildFileStem()}-report.json`,
      JSON.stringify(payload, null, 2),
      "application/json;charset=utf-8",
    );
  });

  elements.resetState.addEventListener("click", () => {
    const shouldReset = window.confirm(
      "Сбросить локально сохраненную карточку кейса, отмеченные источники и заметки?",
    );
    if (!shouldReset) {
      return;
    }

    state = cloneDefaultState();
    saveState();
    hydrateForm();
    renderRiskChecklist();
    render();
  });
}

function handleProfileInput(event) {
  const target = event.target;
  if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) {
    return;
  }

  let value = target.value.trim();
  if (target.id === "inn" || target.id === "ogrn") {
    value = value.replace(/[^\d]/g, "");
    target.value = value;
  }

  if (target.id === "domain") {
    value = normalizeDomain(value);
    target.value = value;
  }

  state.profile[target.id] = value;
  saveState();
  render();
}

function handleRiskToggle(event) {
  const target = event.target;
  if (!(target instanceof HTMLInputElement) || target.type !== "checkbox") {
    return;
  }

  const riskId = target.dataset.riskId;
  if (!riskId) {
    return;
  }

  const selected = new Set(state.selectedRisks);
  if (target.checked) {
    selected.add(riskId);
  } else {
    selected.delete(riskId);
  }

  state.selectedRisks = Array.from(selected);
  saveState();
  renderRiskSummary();
  renderBriefingCard();
  updateMetrics();
}

function handleSourceActions(event) {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  const button = target.closest("[data-source-action]");
  if (!button) {
    return;
  }

  const sourceId = button.getAttribute("data-source-id");
  const action = button.getAttribute("data-source-action");

  if (!sourceId || !action) {
    return;
  }

  if (action === "toggle-complete") {
    toggleSourceCompletion(sourceId);
    render();
  }

  if (action === "copy-query") {
    const source = SOURCE_LIBRARY.find((item) => item.id === sourceId);
    if (!source) {
      return;
    }

    copyText(buildQueryHint(source)).then(() => {
      setTemporaryButtonLabel(button, "Скопировано");
    });
  }
}

function handleDashboardToggle(event) {
  const target = event.target;
  if (!(target instanceof HTMLInputElement) || target.type !== "checkbox") {
    return;
  }

  const sourceId = target.dataset.dashboardSourceId;
  if (!sourceId) {
    return;
  }

  toggleSourceCompletion(sourceId);
  render();
}

function toggleSourceCompletion(sourceId) {
  const completed = new Set(state.completedSources);
  if (completed.has(sourceId)) {
    completed.delete(sourceId);
  } else {
    completed.add(sourceId);
  }

  state.completedSources = Array.from(completed);
  saveState();
}

function render() {
  renderWorkflow();
  renderBriefingCard();
  renderSourceLibrary();
  renderRiskSummary();
  renderDashboard();
  updateMetrics();
}

function renderWorkflow() {
  const recommended = getRecommendedSources();

  if (!recommended.length) {
    elements.workflowList.innerHTML = `
      <li>
        <strong>Маршрут пока пуст</strong>
        <span class="muted-copy">Добавьте ИНН, наименование или домен, чтобы получить приоритизированный список источников.</span>
      </li>
    `;
    return;
  }

  elements.workflowList.innerHTML = recommended
    .map((source) => {
      const queryHint = escapeHtml(buildQueryHint(source));
      const outputs = source.outputs
        .map((output) => `<span class="chip">${escapeHtml(output)}</span>`)
        .join("");

      return `
        <li>
          <strong>${escapeHtml(source.name)}</strong>
          <span class="muted-copy">${escapeHtml(source.description)}</span>
          <div class="workflow-meta">
            <span class="chip chip-accent">${escapeHtml(CATEGORY_LABELS[source.category])}</span>
            ${outputs}
          </div>
          <div class="source-hint">Искать по: ${queryHint}</div>
        </li>
      `;
    })
    .join("");
}

function renderBriefingCard() {
  const recommended = getRecommendedSources();
  const summary = getRiskSummary();
  const completed = getCompletedSourceObjects();
  const topSources = recommended.slice(0, 6);

  const profileRows = [
    ["Тип объекта", state.profile.subjectType === "company" ? "ЮЛ" : "ИП"],
    ["Наименование", state.profile.entityName || "Не заполнено"],
    ["ИНН", state.profile.inn || "Не заполнено"],
    ["ОГРН", state.profile.ogrn || "Не заполнено"],
    ["Домен", state.profile.domain || "Не заполнено"],
    ["Отрасль", state.profile.sector || "Не заполнено"],
  ];

  const flags = summary.selected.length
    ? summary.selected.map((item) => `<li>${escapeHtml(item.label)}</li>`).join("")
    : `<li>Существенные risk flags пока не отмечены.</li>`;

  const reviewedSources = completed.length
    ? completed.map((item) => `<li>${escapeHtml(item.name)}</li>`).join("")
    : `<li>Источники еще не отмечены как просмотренные.</li>`;

  const routePreview = topSources.length
    ? topSources.map((item) => `<li>${escapeHtml(item.name)}</li>`).join("")
    : `<li>Маршрут появится после заполнения карточки кейса.</li>`;

  elements.briefingCard.innerHTML = `
    <h4>Карточка кейса</h4>
    <ul>
      ${profileRows
        .map(
          ([label, value]) =>
            `<li><strong>${escapeHtml(label)}:</strong> ${escapeHtml(value)}</li>`,
        )
        .join("")}
    </ul>
    <h4>Приоритетные источники</h4>
    <ol>${routePreview}</ol>
    <h4>Текущий риск-профиль</h4>
    <ul>
      <li><strong>Risk score:</strong> ${summary.score}</li>
      <li><strong>Уровень:</strong> ${escapeHtml(summary.level)}</li>
      ${flags}
    </ul>
    <h4>Просмотренные источники</h4>
    <ul>${reviewedSources}</ul>
  `;
}

function renderSourceLibrary() {
  const visibleSources = getVisibleSources();
  const recommended = new Set(getRecommendedSources().map((source) => source.id));

  elements.sourceStats.innerHTML = `
    Показано источников: <strong>${visibleSources.length}</strong>
    · Рекомендовано текущему кейсу: <strong>${recommended.size}</strong>
    · Просмотрено: <strong>${getCompletedSourceObjects().length}</strong>
  `;

  if (!visibleSources.length) {
    elements.sourceGrid.innerHTML = `
      <div class="empty-state">
        По текущим фильтрам ничего не найдено. Попробуйте снять фильтр категории или переключить режим "Только официальные".
      </div>
    `;
    return;
  }

  elements.sourceGrid.innerHTML = visibleSources
    .map((source) => {
      const isRecommended = recommended.has(source.id);
      const isCompleted = state.completedSources.includes(source.id);
      const isContextual = !isRecommended && sourceVisibleForSubject(source);
      const queryHint = buildQueryHint(source);

      return `
        <article class="source-card">
          <div class="source-card-top">
            <span class="chip chip-accent">${escapeHtml(CATEGORY_LABELS[source.category])}</span>
            <span class="chip">${source.official ? "Официальный источник" : "Публичный источник"}</span>
            ${isRecommended ? `<span class="status-badge status-recommended">В маршруте</span>` : ""}
            ${isContextual ? `<span class="status-badge status-contextual">Контекстный источник</span>` : ""}
            ${isCompleted ? `<span class="status-badge status-complete">Просмотрено</span>` : ""}
          </div>

          <div>
            <h3>${escapeHtml(source.name)}</h3>
            <p>${escapeHtml(source.description)}</p>
          </div>

          <div class="source-card-tags">
            ${source.outputs.map((output) => `<span class="chip">${escapeHtml(output)}</span>`).join("")}
          </div>

          <div class="source-hint">
            Подставить в поиск: <strong>${escapeHtml(queryHint)}</strong>
          </div>

          <div class="source-card-actions">
            <a class="button small" href="${source.url}" target="_blank" rel="noreferrer noopener">
              Открыть источник
            </a>

            <div class="button-group">
              <button
                class="button small ghost"
                type="button"
                data-source-action="copy-query"
                data-source-id="${source.id}"
              >
                Скопировать запрос
              </button>
              <button
                class="button small ghost"
                type="button"
                data-source-action="toggle-complete"
                data-source-id="${source.id}"
              >
                ${isCompleted ? "Снять отметку" : "Пометить просмотренным"}
              </button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderRiskChecklist() {
  elements.riskList.innerHTML = RISK_ITEMS.map((item) => {
    const checked = state.selectedRisks.includes(item.id) ? "checked" : "";
    return `
      <label class="risk-item">
        <input type="checkbox" data-risk-id="${item.id}" ${checked} />
        <div>
          <div class="chip">${escapeHtml(item.category)}</div>
          <h3>${escapeHtml(item.label)}</h3>
          <p>${escapeHtml(item.note)}</p>
          <div class="risk-item-note">${escapeHtml(item.action)}</div>
        </div>
        <span class="risk-weight">+${item.weight}</span>
      </label>
    `;
  }).join("");
}

function renderRiskSummary() {
  const summary = getRiskSummary();
  elements.riskScore.textContent = String(summary.score);
  elements.riskLevel.textContent = summary.level;
  elements.riskExplainer.textContent = summary.explainer;

  elements.riskBadge.classList.remove("risk-low", "risk-moderate", "risk-high");
  elements.riskBadge.classList.add(summary.badgeClass);

  elements.riskFlags.innerHTML = summary.selected.length
    ? summary.selected.map((item) => `<li>${escapeHtml(item.label)}</li>`).join("")
    : `<li>Отметьте наблюдения из реестров, чтобы зафиксировать флаги.</li>`;

  elements.riskActions.innerHTML = summary.actions
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
}

function renderDashboard() {
  const recommended = getRecommendedSources();
  const lanes = Object.keys(LANE_LABELS).map((laneKey) => ({
    key: laneKey,
    title: LANE_LABELS[laneKey],
    items: recommended.filter((source) => source.lane === laneKey),
  }));

  elements.dashboardBoard.innerHTML = lanes
    .map((lane) => {
      const completedCount = lane.items.filter((item) => state.completedSources.includes(item.id)).length;
      const progressText = lane.items.length
        ? `${completedCount} из ${lane.items.length} источников отмечено`
        : "Нет обязательных источников для текущего профиля";

      const itemsMarkup = lane.items.length
        ? lane.items
            .map((source) => {
              const checked = state.completedSources.includes(source.id) ? "checked" : "";
              return `
                <label class="dashboard-item">
                  <input type="checkbox" data-dashboard-source-id="${source.id}" ${checked} />
                  <div>
                    <strong>${escapeHtml(source.name)}</strong>
                    <span>${escapeHtml(buildQueryHint(source))}</span>
                  </div>
                </label>
              `;
            })
            .join("")
        : `<div class="empty-state">На этой глубине проверки дополнительные действия не требуются.</div>`;

      return `
        <article class="dashboard-column">
          <h3>${escapeHtml(lane.title)}</h3>
          <div class="lane-progress">${escapeHtml(progressText)}</div>
          <div class="dashboard-items">${itemsMarkup}</div>
        </article>
      `;
    })
    .join("");
}

function updateMetrics() {
  elements.metricRecommended.textContent = String(getRecommendedSources().length);
  elements.metricCompleted.textContent = String(getCompletedSourceObjects().length);
  elements.metricRisk.textContent = String(getRiskSummary().score);
}

function getVisibleSources() {
  const query = elements.sourceSearch.value.trim().toLowerCase();
  const category = elements.categoryFilter.value;
  const officialOnly = elements.officialOnly.checked;

  return SOURCE_LIBRARY.filter((source) => {
    if (!sourceVisibleForSubject(source)) {
      return false;
    }

    if (category !== "all" && source.category !== category) {
      return false;
    }

    if (officialOnly && !source.official) {
      return false;
    }

    if (!query) {
      return true;
    }

    const haystack = [
      source.name,
      source.description,
      CATEGORY_LABELS[source.category],
      source.outputs.join(" "),
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(query);
  }).sort((left, right) => left.order - right.order);
}

function getRecommendedSources() {
  return SOURCE_LIBRARY.filter((source) => {
    if (!sourceVisibleForSubject(source)) {
      return false;
    }

    if (STAGE_RANK[source.minStage] > STAGE_RANK[state.profile.stage]) {
      return false;
    }

    if (Array.isArray(source.profiles) && !source.profiles.includes(state.profile.regulatoryProfile)) {
      return false;
    }

    if (Array.isArray(source.requiresAny)) {
      const hasAny = source.requiresAny.some((field) => Boolean(cleanValue(state.profile[field])));
      if (!hasAny) {
        return false;
      }
    }

    return true;
  }).sort((left, right) => left.order - right.order);
}

function getCompletedSourceObjects() {
  const completed = new Set(state.completedSources);
  return SOURCE_LIBRARY.filter(
    (source) => completed.has(source.id) && sourceVisibleForSubject(source),
  ).sort((left, right) => left.order - right.order);
}

function sourceVisibleForSubject(source) {
  return source.subjects.includes(state.profile.subjectType);
}

function getRiskSummary() {
  const selected = RISK_ITEMS.filter((item) => state.selectedRisks.includes(item.id));
  const score = selected.reduce((sum, item) => sum + item.weight, 0);

  let level = "Низкий";
  let explainer =
    "Отмеченные признаки пока не указывают на существенные red flags.";
  let badgeClass = "risk-low";

  if (score >= 100) {
    level = "Высокий";
    explainer =
      "Набор флагов требует обязательной эскалации на углубленную юридическую и комплаенс-проверку.";
    badgeClass = "risk-high";
  } else if (score >= 60) {
    level = "Повышенный";
    explainer =
      "Есть несколько существенных признаков риска. Не принимайте решение без пояснений и подтверждающих документов.";
    badgeClass = "risk-high";
  } else if (score >= 25) {
    level = "Средний";
    explainer =
      "Нужны адресные уточнения по отмеченным сигналам и документальное подтверждение ключевых фактов.";
    badgeClass = "risk-moderate";
  }

  const bucketActions = {
    low: [
      "Продолжить стандартную проверку и сохранить ссылки на источники в отчете.",
    ],
    moderate: [
      "Запросить пояснения и подтверждающие документы по отмеченным risk flags.",
      "Сверить сведения минимум по двум независимым источникам.",
    ],
    high: [
      "Эскалировать кейс на юридическую или комплаенс-проверку.",
      "Не завершать онбординг до закрытия существенных вопросов по рискам.",
    ],
  };

  const bucketKey = score >= 60 ? "high" : score >= 25 ? "moderate" : "low";
  const actions = Array.from(
    new Set([...bucketActions[bucketKey], ...selected.map((item) => item.action)]),
  );

  return {
    score,
    level,
    explainer,
    badgeClass,
    selected,
    actions,
  };
}

function buildQueryHint(source) {
  const profile = state.profile;

  if (source.id === "whois") {
    return profile.domain
      ? profile.domain
      : "Добавьте домен компании, чтобы включить источник в маршрут";
  }

  if (source.id === "media") {
    const parts = [
      profile.entityName ? `"${profile.entityName}"` : "",
      profile.inn ? `ИНН ${profile.inn}` : "",
      profile.domain || "",
    ].filter(Boolean);

    return parts.length
      ? parts.join(" OR ")
      : "Добавьте название компании или ИНН для медиапоиска";
  }

  if (source.id === "ofac") {
    if (profile.entityName) {
      return `${profile.entityName} (при необходимости - латиницей)`;
    }

    return "Название контрагента латиницей или алиасы";
  }

  const availableFields = source.fields
    .map((field) => {
      const value = cleanValue(profile[field]);
      if (!value) {
        return null;
      }

      return `${FIELD_LABELS[field]}: ${value}`;
    })
    .filter(Boolean);

  if (availableFields.length) {
    return availableFields.join(" | ");
  }

  return source.fields
    .map((field) => FIELD_LABELS[field])
    .filter(Boolean)
    .join(" / ");
}

function buildBriefingMarkdown() {
  const recommended = getRecommendedSources();
  const summary = getRiskSummary();
  const completed = getCompletedSourceObjects();

  const lines = [
    `# Краткий бриф: ${buildCaseName()}`,
    "",
    "## Профиль кейса",
    `- Тип объекта: ${state.profile.subjectType === "company" ? "ЮЛ" : "ИП"}`,
    `- Наименование: ${state.profile.entityName || "Не заполнено"}`,
    `- ИНН: ${state.profile.inn || "Не заполнено"}`,
    `- ОГРН: ${state.profile.ogrn || "Не заполнено"}`,
    `- Домен: ${state.profile.domain || "Не заполнено"}`,
    `- Отрасль: ${state.profile.sector || "Не заполнено"}`,
    `- Регуляторный профиль: ${getRegulatoryProfileLabel(state.profile.regulatoryProfile)}`,
    `- Глубина проверки: ${getStageLabel(state.profile.stage)}`,
    "",
    "## Рекомендуемый маршрут",
    ...recommended.map(
      (source, index) =>
        `${index + 1}. ${source.name} — искать по: ${buildQueryHint(source)}`,
    ),
    "",
    "## Текущий risk profile",
    `- Risk score: ${summary.score}`,
    `- Уровень: ${summary.level}`,
    ...(summary.selected.length
      ? summary.selected.map((item) => `- ${item.label}`)
      : ["- Существенные risk flags пока не отмечены"]),
    "",
    "## Уже просмотренные источники",
    ...(completed.length
      ? completed.map((source) => `- ${source.name}`)
      : ["- Источники пока не отмечены"]),
  ];

  return lines.join("\n");
}

function buildFullReportMarkdown() {
  const recommended = getRecommendedSources();
  const completed = getCompletedSourceObjects();
  const summary = getRiskSummary();

  const lines = [
    `# Нейтральный OSINT-отчет: ${buildCaseName()}`,
    "",
    "## Ограничения использования",
    "- Отчет предназначен для проверки компаний и ИП по открытым источникам.",
    "- Не использовать для профилирования частных лиц или составления досье на людей.",
    "",
    "## Карточка объекта",
    `- Тип объекта: ${state.profile.subjectType === "company" ? "ЮЛ" : "ИП"}`,
    `- Наименование: ${state.profile.entityName || "Не заполнено"}`,
    `- ИНН: ${state.profile.inn || "Не заполнено"}`,
    `- ОГРН: ${state.profile.ogrn || "Не заполнено"}`,
    `- Домен: ${state.profile.domain || "Не заполнено"}`,
    `- Телефон организации: ${state.profile.orgPhone || "Не заполнено"}`,
    `- Регион: ${state.profile.region || "Не заполнено"}`,
    `- Отрасль / ОКВЭД: ${state.profile.sector || "Не заполнено"}`,
    `- Регуляторный профиль: ${getRegulatoryProfileLabel(state.profile.regulatoryProfile)}`,
    `- Глубина проверки: ${getStageLabel(state.profile.stage)}`,
    "",
    "## Цель проверки",
    state.notes.caseGoal || "Не заполнено",
    "",
    "## Рекомендуемые источники",
    ...recommended.map(
      (source, index) =>
        `${index + 1}. ${source.name} (${CATEGORY_LABELS[source.category]}) - ${buildQueryHint(source)}`,
    ),
    "",
    "## Просмотренные источники",
    ...(completed.length
      ? completed.map((source) => `- ${source.name}`)
      : ["- Источники пока не отмечены"]),
    "",
    "## Risk summary",
    `- Risk score: ${summary.score}`,
    `- Уровень: ${summary.level}`,
    `- Пояснение: ${summary.explainer}`,
    ...(summary.selected.length
      ? summary.selected.map((item) => `- ${item.label}`)
      : ["- Дополнительные risk flags не отмечены"]),
    "",
    "## Подтвержденные факты из открытых источников",
    state.notes.confirmedFacts || "Не заполнено",
    "",
    "## Нейтральное заключение",
    state.notes.conclusion || "Не заполнено",
    "",
    "## Следующие шаги",
    state.notes.nextSteps || "Не заполнено",
    "",
    "## Рекомендуемые действия по рискам",
    ...summary.actions.map((action) => `- ${action}`),
  ];

  return lines.join("\n");
}

function buildCaseName() {
  return state.profile.entityName || state.profile.inn || "новый-контрагент";
}

function buildFileStem() {
  return slugify(buildCaseName());
}

function getStageLabel(stage) {
  return {
    express: "Экспресс",
    standard: "Стандарт",
    deep: "Углубленная",
  }[stage];
}

function getRegulatoryProfileLabel(profile) {
  return {
    general: "Общий профиль",
    licensed: "Лицензируемая деятельность",
    finance: "Финансовая организация",
  }[profile];
}

function cleanValue(value) {
  return typeof value === "string" ? value.trim() : "";
}

function cloneDefaultState() {
  return JSON.parse(JSON.stringify(DEFAULT_STATE));
}

function normalizeDomain(value) {
  return value
    .replace(/^https?:\/\//i, "")
    .replace(/\/.*$/, "")
    .replace(/\s+/g, "")
    .toLowerCase();
}

function slugify(value) {
  return String(value)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9а-яё]+/gi, "-")
    .replace(/^-+|-+$/g, "") || "rf-due-diligence";
}

async function copyText(value) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(value);
    return;
  }

  const helper = document.createElement("textarea");
  helper.value = value;
  helper.setAttribute("readonly", "");
  helper.style.position = "absolute";
  helper.style.left = "-9999px";
  document.body.appendChild(helper);
  helper.select();
  document.execCommand("copy");
  document.body.removeChild(helper);
}

function downloadFile(filename, content, mimeType = "text/markdown;charset=utf-8") {
  const blob = new Blob([content], { type: mimeType });
  const link = document.createElement("a");
  const objectUrl = URL.createObjectURL(blob);
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
}

function setTemporaryButtonLabel(button, label) {
  const element = button instanceof HTMLElement ? button : null;
  if (!element) {
    return;
  }

  const original = element.textContent;
  element.textContent = label;
  window.setTimeout(() => {
    element.textContent = original;
  }, 1400);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
