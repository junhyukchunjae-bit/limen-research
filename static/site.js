// 보고서 아카이브의 분야 필터. 주소의 ?sector=키 로 바로 걸러진 화면을 열 수 있다.
document.addEventListener("DOMContentLoaded", () => {
  const chips = [...document.querySelectorAll(".chip[data-filter]")];
  if (!chips.length) return;
  const rows = document.querySelectorAll(".entries .entry");

  const apply = (key) => {
    chips.forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.filter === key)));
    rows.forEach((r) => {
      r.hidden = Boolean(key) && !r.dataset.sectors.split(" ").includes(key);
    });
  };

  chips.forEach((c) =>
    c.addEventListener("click", () => {
      apply(c.dataset.filter);
      const url = new URL(location.href);
      if (c.dataset.filter) url.searchParams.set("sector", c.dataset.filter);
      else url.searchParams.delete("sector");
      history.replaceState(null, "", url);
    })
  );

  const initial = new URLSearchParams(location.search).get("sector") || "";
  if (chips.some((c) => c.dataset.filter === initial)) apply(initial);
});
