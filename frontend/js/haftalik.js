"use strict";
/* HAFTALIK MENÜ VE REZERVASYON
   Düğmenin aktif/pasif olması ve yazısı API'den gelir (yapilabilir, pasiflik_nedeni); burada kural yoktur. */

const kullanici = sayfaBaslat("haftalik.html");
if (kullanici) basla();

async function basla() {
  const kutu = document.getElementById("bildirim");
  const yemekhaneSecimi = document.getElementById("yemekhane");
  const baslangicGirdisi = document.getElementById("baslangic");
  const icerik = document.getElementById("icerik");

  try {
    const secenekler = await api("/secenekler");
    for (const y of secenekler.yemekhaneler)
      yemekhaneSecimi.append(el("option", { value: y.id }, y.ad));
    baslangicGirdisi.value = secenekler.bugun;
  } catch (h) {
    bildir(kutu, h.message, "hata");
    return;
  }

  async function yukle(taze) {
    if (!baslangicGirdisi.value) return;
    const sorgu = new URLSearchParams({
      yemekhane_id: yemekhaneSecimi.value,
      baslangic: baslangicGirdisi.value,
    });
    if (taze) sorgu.set("taze", "1");
    try {
      const sonuc = await api("/menu/haftalik?" + sorgu);
      ciz(sonuc.menuler);
    } catch (h) {
      icerik.replaceChildren();
      bildir(kutu, h.message, "hata");
    }
  }

  function ciz(menuler) {
    if (menuler.length === 0) {
      icerik.replaceChildren(
        el("p", { sinif: "soluk" }, "Bu tarih aralığında menü yok."),
      );
      return;
    }
    const gunler = new Map();
    for (const m of menuler) {
      if (!gunler.has(m.tarih)) gunler.set(m.tarih, []);
      gunler.get(m.tarih).push(m);
    }
    icerik.replaceChildren(
      ...[...gunler].map(([tarih, liste]) =>
        el(
          "section",
          { sinif: "kart" },
          el(
            "h2",
            { sinif: "gun-baslik", style: "margin-top:0" },
            gunYaz(tarih),
          ),
          liste.map(ogunSatiri),
        ),
      ),
    );
  }

  function ogunSatiri(m) {
    const dugme = el(
      "button",
      {
        type: "button",
        sinif: "dugme dugme-kucuk",
        disabled: !m.yapilabilir,
        onclick: () => rezerveEt(m, dugme),
      },
      m.yapilabilir ? "Rezervasyon yap" : m.pasiflik_nedeni,
    );

    return el(
      "div",
      { sinif: "ogun-satiri" },
      el(
        "div",
        {},
        el("strong", {}, m.ogun),
        " ",
        el(
          "span",
          { sinif: "soluk kucuk" },
          "son saat " + saatYaz(m.rezervasyon_son),
        ),
        el("p", { sinif: "yemekler" }, m.yemekler),
      ),
      el(
        "div",
        { sinif: "ogun-alt" },
        el("span", { sinif: "fiyat" }, para(m.fiyat)),
        el("span", { sinif: "kucuk" }, "Boş: " + m.bos_yer),
        m.rezervasyon_durumu ? durumRozeti(m.rezervasyon_durumu) : null,
        dugme,
      ),
    );
  }

  async function rezerveEt(menu, dugme) {
    dugme.disabled = true;
    bildirimiGizle(kutu);
    try {
      const sonuc = await api("/rezervasyon", {
        metod: "POST",
        govde: { menu_id: menu.menu_id },
      });
      bildir(
        kutu,
        "Rezervasyon yapıldı. Ücret: " +
          para(sonuc.ucret) +
          " · Yeni bakiyeniz: " +
          para(sonuc.bakiye),
        "basari",
      );
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
    await yukle(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function haftaKaydir(gun) {
    const d = new Date(baslangicGirdisi.value + "T00:00:00Z");
    d.setUTCDate(d.getUTCDate() + gun);
    baslangicGirdisi.value = d.toISOString().slice(0, 10);
    bildirimiGizle(kutu);
    yukle(false);
  }

  yemekhaneSecimi.addEventListener("change", () => {
    bildirimiGizle(kutu);
    yukle(false);
  });
  baslangicGirdisi.addEventListener("change", () => {
    bildirimiGizle(kutu);
    yukle(false);
  });
  document
    .getElementById("onceki")
    .addEventListener("click", () => haftaKaydir(-7));
  document
    .getElementById("sonraki")
    .addEventListener("click", () => haftaKaydir(7));
  yukle(false);
}
