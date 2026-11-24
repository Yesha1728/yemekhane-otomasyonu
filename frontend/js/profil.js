"use strict";
/* PROFİL: kullanıcı alerjenlerini seçer. Seçim API'ye gider (kaynağa yazılır); kural ve doğrulama API'dedir. */

const kullanici = sayfaBaslat("profil.html");
if (kullanici) basla();

function basla() {
  const kutu = document.getElementById("bildirim");
  const liste = document.getElementById("alerjen-listesi");
  const form = document.getElementById("alerjen-formu");

  function ciz(alerjenler) {
    liste.replaceChildren(
      ...alerjenler.map((a) =>
        el(
          "label",
          { sinif: "onay-satiri" },
          el("input", { type: "checkbox", value: a.id, checked: a.secili }),
          el("span", {}, a.ad),
        ),
      ),
    );
  }

  async function yukle() {
    try {
      const sonuc = await api("/profil/alerjenler");
      ciz(sonuc.alerjenler);
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
  }

  form.addEventListener("submit", async (olay) => {
    olay.preventDefault();
    bildirimiGizle(kutu);
    const idler = [...liste.querySelectorAll("input:checked")].map((x) =>
      Number(x.value),
    );
    try {
      const sonuc = await api("/profil/alerjenler", {
        metod: "POST",
        govde: { alerjen_idler: idler },
      });
      ciz(sonuc.alerjenler);
      bildir(
        kutu,
        idler.length === 0
          ? "Alerjen seçiminiz temizlendi."
          : "Alerjenleriniz kaydedildi (" + idler.length + " seçili).",
        "basari",
      );
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
  });

  yukle();
}
