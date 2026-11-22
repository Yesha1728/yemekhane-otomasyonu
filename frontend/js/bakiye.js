"use strict";
/* BAKİYE: güncel bakiye, hareket geçmişi, bakiye yükleme.
   Yükleme tutarının 10-1000 TL kuralını sp_bakiye_yukle denetler; mesajı olduğu gibi gösteririz. */

const kullanici = sayfaBaslat("bakiye.html");
if (kullanici) basla();

const TUR_ETIKET = {
  yukleme: "Yükleme",
  rezervasyon: "Rezervasyon",
  iade: "İade",
};

function basla() {
  const kutu = document.getElementById("bildirim");
  const bakiyeKutusu = document.getElementById("bakiye");
  const hareketler = document.getElementById("hareketler");
  const form = document.getElementById("yukle-formu");
  const tutarGirdisi = document.getElementById("tutar");

  async function yukle(taze) {
    try {
      const sonuc = await api("/bakiye" + (taze ? "?taze=1" : ""));
      bakiyeKutusu.textContent = para(sonuc.bakiye);
      hareketleriCiz(sonuc.hareketler);
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
  }

  function hareketleriCiz(liste) {
    if (liste.length === 0) {
      hareketler.replaceChildren(
        el("p", { sinif: "soluk" }, "Henüz hareket yok."),
      );
      return;
    }
    hareketler.replaceChildren(
      el(
        "table",
        { sinif: "tablo" },
        el(
          "thead",
          {},
          el(
            "tr",
            {},
            el("th", {}, "Tarih"),
            el("th", {}, "Tür"),
            el("th", { sinif: "sag" }, "Tutar"),
            el("th", {}, "Açıklama"),
          ),
        ),
        el(
          "tbody",
          {},
          liste.map((h) =>
            el(
              "tr",
              {},
              el("td", {}, zamanYaz(h.olusturma)),
              el("td", {}, TUR_ETIKET[h.tur] || h.tur),
              el(
                "td",
                { sinif: "sag " + (h.tutar >= 0 ? "pozitif" : "negatif") },
                (h.tutar > 0 ? "+" : "") + para(h.tutar),
              ),
              el("td", {}, h.aciklama || ""),
            ),
          ),
        ),
      ),
    );
  }

  form.addEventListener("submit", async (olay) => {
    olay.preventDefault();
    bildirimiGizle(kutu);
    try {
      const sonuc = await api("/bakiye/yukle", {
        metod: "POST",
        govde: { tutar: tutarGirdisi.value.trim().replace(",", ".") },
      });
      bildir(
        kutu,
        "Bakiye yüklendi. Yeni bakiyeniz: " + para(sonuc.bakiye),
        "basari",
      );
      tutarGirdisi.value = "";
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
    await yukle(true);
  });

  yukle(false);
}
