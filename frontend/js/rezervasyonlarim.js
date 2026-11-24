"use strict";
/* REZERVASYONLARIM: aktif, kullanıldı ve iptal durumları; süresi dolmamışsa iptal. */

const PORSIYON_ETIKET = { tam: "Tam porsiyon", yarim: "Yarım porsiyon" };

const kullanici = sayfaBaslat("rezervasyonlarim.html");
if (kullanici) basla();

function basla() {
  const kutu = document.getElementById("bildirim");
  const icerik = document.getElementById("icerik");

  async function yukle(taze) {
    try {
      const sonuc = await api("/rezervasyonlarim" + (taze ? "?taze=1" : ""));
      ciz(sonuc.rezervasyonlar);
    } catch (h) {
      icerik.replaceChildren();
      bildir(kutu, h.message, "hata");
    }
  }

  function ciz(liste) {
    if (liste.length === 0) {
      icerik.replaceChildren(
        el("p", { sinif: "soluk" }, "Henüz rezervasyonunuz yok. "),
        el(
          "a",
          { href: "/haftalik.html" },
          "Haftalık menüden rezervasyon yapın →",
        ),
      );
      return;
    }
    icerik.replaceChildren(...liste.map(kart));
  }

  function kart(r) {
    return el(
      "article",
      { sinif: "kart rezervasyon-kart" },
      el(
        "div",
        { sinif: "ust" },
        el("strong", {}, kisaGunYaz(r.tarih) + " · " + r.ogun),
        durumRozeti(r.durum),
      ),
      el("div", { sinif: "soluk kucuk" }, r.yemekhane),
      el("div", {}, "Porsiyon: ", PORSIYON_ETIKET[r.porsiyon] || r.porsiyon),
      el("div", {}, "Ücret: ", el("span", { sinif: "fiyat" }, para(r.ucret))),
      r.durum === "kullanildi" && r.kullanma_zamani
        ? el(
            "div",
            { sinif: "kucuk soluk" },
            "Kullanım: " + zamanYaz(r.kullanma_zamani),
          )
        : null,
      r.durum === "iptal" && r.iptal_zamani
        ? el(
            "div",
            { sinif: "kucuk soluk" },
            "İptal: " + zamanYaz(r.iptal_zamani),
          )
        : null,
      r.durum === "aktif"
        ? el(
            "div",
            { sinif: "kucuk soluk" },
            "Son iptal saati: " + zamanYaz(r.rezervasyon_son),
          )
        : null,
      r.iptal_edilebilir
        ? el(
            "div",
            {},
            el(
              "button",
              {
                type: "button",
                sinif: "dugme dugme-tehlike dugme-kucuk",
                onclick: () => iptalEt(r),
              },
              "İptal et",
            ),
          )
        : null,
    );
  }

  async function iptalEt(r) {
    if (
      !confirm(
        kisaGunYaz(r.tarih) + " " + r.ogun + " rezervasyonu iptal edilsin mi?",
      )
    )
      return;
    bildirimiGizle(kutu);
    try {
      const sonuc = await api("/rezervasyon/" + r.rezervasyon_id + "/iptal", {
        metod: "POST",
      });
      bildir(
        kutu,
        "Rezervasyon iptal edildi. İade: " +
          para(sonuc.iade) +
          " · Yeni bakiyeniz: " +
          para(sonuc.bakiye),
        "basari",
      );
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
    await yukle(true);
  }

  yukle(false);
}
