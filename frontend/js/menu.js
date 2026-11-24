"use strict";
/* GÜNÜN MENÜSÜ: yemekhane, öğün ve tarih seçilir; yemekler, toplam kalori, vejetaryen ve alerjen bilgisi gösterilir.
   Alerjen uyarısı API'den gelir (uyari_alerjenleri); burada kural yoktur. */

const kullanici = sayfaBaslat("menu.html");
if (kullanici) basla();

async function basla() {
  const kutu = document.getElementById("bildirim");
  const yemekhaneSecimi = document.getElementById("yemekhane");
  const ogunSecimi = document.getElementById("ogun");
  const tarihGirdisi = document.getElementById("tarih");
  const icerik = document.getElementById("icerik");

  try {
    const secenekler = await api("/secenekler");
    for (const y of secenekler.yemekhaneler)
      yemekhaneSecimi.append(el("option", { value: y.id }, y.ad));
    for (const o of secenekler.ogunler)
      ogunSecimi.append(el("option", { value: o.id }, o.ad));
    ogunSecimi.value = "2"; // açılışta öğle
    tarihGirdisi.value = secenekler.bugun;
  } catch (h) {
    bildir(kutu, h.message, "hata");
    return;
  }

  async function yukle() {
    bildirimiGizle(kutu);
    if (!tarihGirdisi.value) return;
    const sorgu = new URLSearchParams({
      yemekhane_id: yemekhaneSecimi.value,
      ogun_id: ogunSecimi.value,
      tarih: tarihGirdisi.value,
    });
    icerik.replaceChildren(el("p", { sinif: "soluk" }, "Yükleniyor…"));
    try {
      const menu = await api("/menu/gunluk?" + sorgu);
      icerik.replaceChildren(menuKarti(menu));
    } catch (h) {
      icerik.replaceChildren();
      bildir(kutu, h.message, "hata");
    }
  }

  for (const alan of [yemekhaneSecimi, ogunSecimi, tarihGirdisi])
    alan.addEventListener("change", yukle);
  yukle();
}

function menuKarti(menu) {
  const kategoriler = [];
  for (const y of menu.yemekler) {
    let grup = kategoriler[kategoriler.length - 1];
    if (!grup || grup.ad !== y.kategori) {
      grup = { ad: y.kategori, yemekler: [] };
      kategoriler.push(grup);
    }
    grup.yemekler.push(y);
  }
  const uyarili = menu.yemekler.filter(
    (y) => y.uyari_alerjenleri.length > 0,
  ).length;

  return el(
    "article",
    { sinif: "kart" },
    el("h2", {}, menu.yemekhane + " · " + menu.ogun),
    el("p", { sinif: "soluk" }, gunYaz(menu.tarih)),
    uyarili > 0
      ? el(
          "div",
          { sinif: "bildirim bildirim-hata", role: "alert" },
          "⚠ Alerjen uyarısı: bu menüde " +
            menu.uyari_alerjenleri.join(", ") +
            " içeren " +
            uyarili +
            " yemek var.",
        )
      : null,
    el(
      "div",
      { sinif: "ozet" },
      kutuOge("Fiyatınız", el("span", { sinif: "fiyat" }, para(menu.fiyat))),
      kutuOge("Toplam kalori", menu.toplam_kalori + " kcal"),
      kutuOge("Boş yer", menu.bos_yer + " / " + menu.kapasite),
      kutuOge(
        "Son rezervasyon",
        saatYaz(menu.rezervasyon_son) +
          (menu.suresi_doldu ? " (süre doldu)" : ""),
      ),
    ),
    menu.tamami_vejetaryen
      ? el(
          "p",
          {},
          el("span", { sinif: "rozet rozet-yesil" }, "Tamamı vejetaryen"),
        )
      : null,
    kategoriler.map((grup) =>
      el(
        "div",
        {},
        el("h3", { sinif: "kategori" }, grup.ad),
        grup.yemekler.map(yemekSatiri),
      ),
    ),
    el(
      "p",
      { sinif: "kucuk", style: "margin-top:1rem" },
      el(
        "a",
        { href: "/haftalik.html" },
        "Rezervasyon için haftalık menüye git →",
      ),
    ),
  );
}

function kutuOge(baslik, deger) {
  return el("div", {}, el("small", {}, baslik), el("strong", {}, deger));
}

function yemekSatiri(y) {
  const uyari = y.uyari_alerjenleri.length > 0;
  return el(
    "div",
    { sinif: "yemek" + (uyari ? " yemek-uyarili" : "") },
    el("span", { sinif: "ad" }, y.yemek),
    el("span", { sinif: "kalori" }, y.kalori + " kcal"),
    uyari
      ? el(
          "span",
          { sinif: "rozet rozet-hata" },
          "⚠ Alerjeniniz var: " + y.uyari_alerjenleri.join(", "),
        )
      : null,
    y.vejetaryen
      ? el("span", { sinif: "rozet rozet-yesil" }, "Vejetaryen")
      : null,
    y.alerjenler.map((a) =>
      el("span", { sinif: "rozet rozet-alerjen", title: "Alerjen" }, a),
    ),
  );
}
