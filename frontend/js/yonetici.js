"use strict";
/* YÖNETİCİ PANELİ: menü oluşturma ve düzenleme, menü bazında doluluk ve ortalama puan, turnike denemesi.
   Yetki denetimi sunucudadır (yönetici olmayan kullanıcıya API 403 döner). */

const kullanici = sayfaBaslat("yonetici.html", { yonetici: true });
if (kullanici) basla();

async function basla() {
  const kutu = document.getElementById("bildirim");
  const liste = document.getElementById("liste");

  // süzgeç
  const fYemekhane = document.getElementById("f-yemekhane");
  const fBaslangic = document.getElementById("f-baslangic");
  const fBitis = document.getElementById("f-bitis");

  // menü formu
  const form = document.getElementById("menu-formu");
  const formBaslik = document.getElementById("form-baslik");
  const mYemekhane = document.getElementById("m-yemekhane");
  const mOgun = document.getElementById("m-ogun");
  const mTarih = document.getElementById("m-tarih");
  const mOgrenci = document.getElementById("m-ogrenci");
  const mPersonel = document.getElementById("m-personel");
  const mYemekler = document.getElementById("m-yemekler");
  const mKaydet = document.getElementById("m-kaydet");
  const mVazgec = document.getElementById("m-vazgec");

  // turnike formu
  const tForm = document.getElementById("turnike-formu");
  const tKullanici = document.getElementById("t-kullanici");
  const tYemekhane = document.getElementById("t-yemekhane");
  const tZaman = document.getElementById("t-zaman");

  let duzenlenen = null;

  // seçenekleri doldur
  try {
    const sec = await api("/secenekler");
    const katalog = await api("/yonetici/yemekler");

    fYemekhane.append(el("option", { value: "" }, "Tüm yemekhaneler"));
    for (const y of sec.yemekhaneler) {
      fYemekhane.append(el("option", { value: y.id }, y.ad));
      mYemekhane.append(el("option", { value: y.id }, y.ad));
      tYemekhane.append(el("option", { value: y.id }, y.ad));
    }
    for (const o of sec.ogunler)
      mOgun.append(el("option", { value: o.id }, o.ad));

    const kategoriler = new Map();
    for (const y of katalog.yemekler) {
      if (!kategoriler.has(y.kategori)) kategoriler.set(y.kategori, []);
      kategoriler.get(y.kategori).push(y);
    }
    mYemekler.replaceChildren(
      ...[...kategoriler].map(([ad, yemekler]) =>
        el(
          "fieldset",
          {},
          el("legend", {}, ad),
          yemekler.map((y) =>
            el(
              "label",
              { sinif: "onay" },
              el("input", {
                type: "checkbox",
                name: "yemek",
                value: y.yemek_id,
              }),
              y.yemek + " (" + y.kalori + " kcal)",
            ),
          ),
        ),
      ),
    );

    fBaslangic.value = gunKaydir(sec.bugun, -7);
    fBitis.value = gunKaydir(sec.bugun, 14);
    mTarih.value = sec.bugun;
  } catch (h) {
    bildir(kutu, h.message, "hata");
    return;
  }

  function gunKaydir(iso, gun) {
    const d = new Date(iso + "T00:00:00Z");
    d.setUTCDate(d.getUTCDate() + gun);
    return d.toISOString().slice(0, 10);
  }

  // menü listesi (rapor: replika)
  async function listeyiYukle(taze) {
    const sorgu = new URLSearchParams({
      baslangic: fBaslangic.value,
      bitis: fBitis.value,
    });
    if (fYemekhane.value) sorgu.set("yemekhane_id", fYemekhane.value);
    if (taze) sorgu.set("taze", "1");
    try {
      const sonuc = await api("/yonetici/menuler?" + sorgu);
      listeyiCiz(sonuc.menuler);
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
  }

  function listeyiCiz(menuler) {
    if (menuler.length === 0) {
      liste.replaceChildren(
        el("p", { sinif: "soluk" }, "Bu aralıkta menü yok."),
      );
      return;
    }
    liste.replaceChildren(
      el(
        "table",
        { sinif: "tablo" },
        el(
          "thead",
          {},
          el(
            "tr",
            {},
            [
              "Tarih",
              "Yemekhane",
              "Öğün",
              "Doluluk",
              "Puan",
              "Fiyat (öğr/per)",
              "",
            ].map((b) => el("th", {}, b)),
          ),
        ),
        el(
          "tbody",
          {},
          menuler.map((m) =>
            el(
              "tr",
              {},
              el("td", {}, kisaGunYaz(m.tarih)),
              el("td", {}, m.yemekhane),
              el("td", {}, m.ogun),
              el(
                "td",
                {},
                m.rezerve + " / " + m.kapasite + " (%" + m.doluluk_yuzde + ")",
              ),
              el(
                "td",
                {},
                m.ortalama_puan === null
                  ? "–"
                  : m.ortalama_puan + " (" + m.oy_sayisi + " oy)",
              ),
              el(
                "td",
                {},
                para(m.ogrenci_fiyati) + " / " + para(m.personel_fiyati),
              ),
              el(
                "td",
                {},
                el(
                  "button",
                  {
                    type: "button",
                    sinif: "dugme dugme-ikincil dugme-kucuk",
                    onclick: () => duzenle(m.menu_id),
                  },
                  "Düzenle",
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  for (const alan of [fYemekhane, fBaslangic, fBitis])
    alan.addEventListener("change", () => listeyiYukle(false));

  // form: yeni menü / düzenleme
  function yemekleriIsaretle(idler) {
    const secili = new Set(idler.map(String));
    for (const kutuk of mYemekler.querySelectorAll('input[name="yemek"]'))
      kutuk.checked = secili.has(kutuk.value);
  }

  function formuSifirla() {
    duzenlenen = null;
    formBaslik.textContent = "Yeni menü";
    mKaydet.textContent = "Menüyü oluştur";
    mVazgec.hidden = true;
    for (const alan of [mYemekhane, mOgun, mTarih]) alan.disabled = false;
    mOgrenci.value = "";
    mPersonel.value = "";
    yemekleriIsaretle([]);
  }

  async function duzenle(menuId) {
    bildirimiGizle(kutu);
    try {
      const m = await api("/yonetici/menu/" + menuId); // düzenleme verisi kaynaktan gelir
      duzenlenen = m.menu_id;
      formBaslik.textContent = "Menüyü düzenle (#" + m.menu_id + ")";
      mKaydet.textContent = "Değişiklikleri kaydet";
      mVazgec.hidden = false;
      mYemekhane.value = m.yemekhane_id;
      mOgun.value = m.ogun_id;
      mTarih.value = m.tarih;
      for (const alan of [mYemekhane, mOgun, mTarih]) alan.disabled = true; // menünün kimliği değişmez
      mOgrenci.value = m.ogrenci_fiyati;
      mPersonel.value = m.personel_fiyati;
      yemekleriIsaretle(m.yemek_idleri);
      document
        .getElementById("form-karti")
        .scrollIntoView({ behavior: "smooth" });
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
  }

  mVazgec.addEventListener("click", formuSifirla);

  form.addEventListener("submit", async (olay) => {
    olay.preventDefault();
    bildirimiGizle(kutu);
    const yemekIdleri = [
      ...mYemekler.querySelectorAll('input[name="yemek"]:checked'),
    ].map((k) => Number(k.value));
    const ortak = {
      ogrenci_fiyati: mOgrenci.value.trim().replace(",", "."),
      personel_fiyati: mPersonel.value.trim().replace(",", "."),
      yemek_idleri: yemekIdleri,
    };
    try {
      if (duzenlenen === null) {
        const sonuc = await api("/yonetici/menu", {
          metod: "POST",
          govde: {
            ...ortak,
            yemekhane_id: mYemekhane.value,
            ogun_id: mOgun.value,
            tarih: mTarih.value,
          },
        });
        bildir(kutu, "Menü oluşturuldu (#" + sonuc.menu_id + ").", "basari");
      } else {
        await api("/yonetici/menu/" + duzenlenen, {
          metod: "PUT",
          govde: ortak,
        });
        bildir(kutu, "Menü güncellendi.", "basari");
      }
      formuSifirla();
      await listeyiYukle(true);
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // turnike denemesi (sp_turnike_gecis)
  tForm.addEventListener("submit", async (olay) => {
    olay.preventDefault();
    bildirimiGizle(kutu);
    try {
      const s = await api("/yonetici/turnike", {
        metod: "POST",
        govde: {
          kullanici_id: tKullanici.value.trim(),
          yemekhane_id: tYemekhane.value,
          zaman: tZaman.value,
        },
      });
      bildir(
        kutu,
        "Turnike geçişi kaydedildi: rezervasyon #" +
          s.rezervasyon_id +
          ", " +
          s.ogun +
          " (menü #" +
          s.menu_id +
          ").",
        "basari",
      );
      await listeyiYukle(true);
    } catch (h) {
      bildir(kutu, h.message, "hata");
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  listeyiYukle(false);
}
