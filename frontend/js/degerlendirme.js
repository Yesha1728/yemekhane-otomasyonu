"use strict";
/* DEĞERLENDİRME: kullanılmış menüye 1-5 puan ve yorum. "Yalnızca kullanılmış menü" kuralını sunucu denetler. */

const kullanici = sayfaBaslat("degerlendirme.html");
if (kullanici) basla();

function basla() {
  const kutu = document.getElementById("bildirim");
  const icerik = document.getElementById("icerik");

  async function yukle(taze) {
    try {
      const sonuc = await api("/degerlendirme" + (taze ? "?taze=1" : ""));
      ciz(sonuc.menuler);
    } catch (h) {
      icerik.replaceChildren();
      bildir(kutu, h.message, "hata");
    }
  }

  function ciz(liste) {
    if (liste.length === 0) {
      icerik.replaceChildren(
        el(
          "p",
          {},
          "Henüz kullandığınız bir menü yok. Turnikeden geçtiğiniz menüler burada görünür.",
        ),
      );
      return;
    }
    icerik.replaceChildren(...liste.map(kart));
  }

  function kart(m) {
    const baslik = el("h2", {}, kisaGunYaz(m.tarih) + " · " + m.ogun);
    const alt = el("p", { sinif: "soluk kucuk" }, m.yemekhane);
    if (m.puan !== null) {
      return el(
        "article",
        { sinif: "kart" },
        baslik,
        alt,
        el(
          "p",
          {},
          el("span", { sinif: "rozet rozet-yesil" }, "Değerlendirdiniz"),
          " ",
          "★".repeat(m.puan) + "☆".repeat(5 - m.puan),
          " (" + m.puan + "/5)",
        ),
        m.yorum ? el("p", {}, m.yorum) : null,
      );
    }
    const puan = el(
      "select",
      { id: "puan-" + m.menu_id },
      el("option", { value: "" }, "Puan seçin"),
      [5, 4, 3, 2, 1].map((n) =>
        el("option", { value: n }, n + " · " + "★".repeat(n)),
      ),
    );
    const yorum = el("textarea", {
      id: "yorum-" + m.menu_id,
      placeholder: "Yorumunuz (isteğe bağlı)",
    });
    const form = el(
      "form",
      {},
      el(
        "div",
        { sinif: "alan" },
        el("label", { for: "puan-" + m.menu_id }, "Puan"),
        puan,
      ),
      el(
        "div",
        { sinif: "alan" },
        el("label", { for: "yorum-" + m.menu_id }, "Yorum"),
        yorum,
      ),
      el("button", { type: "submit", sinif: "dugme dugme-kucuk" }, "Gönder"),
    );
    form.addEventListener("submit", (olay) => {
      olay.preventDefault();
      gonder(m, puan.value, yorum.value);
    });
    return el("article", { sinif: "kart" }, baslik, alt, form);
  }

  async function gonder(m, puan, yorum) {
    bildirimiGizle(kutu);
    try {
      await api("/degerlendirme/ekle", {
        metod: "POST",
        govde: { menu_id: m.menu_id, puan: puan, yorum: yorum },
      });
      bildir(kutu, "Değerlendirmeniz kaydedildi. Teşekkürler!", "basari");
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
    await yukle(true);
  }

  yukle(false);
}
