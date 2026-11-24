"use strict";
/* =====================================================================
   ORTAK ARAÇLAR; tüm sayfalar kullanır
   Arayüz iş kuralı bilmez: yalnızca API'den gelen sonucu gösterir,
   hata mesajlarını olduğu gibi ekrana yazar.
   ===================================================================== */

const ANAHTAR_JETON = "yemekhane_jeton";
const ANAHTAR_KULLANICI = "yemekhane_kullanici";

// oturum (tarayıcıda yalnızca jeton ve kullanıcı özeti saklanır)
function jetonAl() {
  try {
    return localStorage.getItem(ANAHTAR_JETON);
  } catch (h) {
    return null;
  }
}
function kullaniciAl() {
  try {
    return JSON.parse(localStorage.getItem(ANAHTAR_KULLANICI));
  } catch (h) {
    return null;
  }
}
function oturumKaydet(jeton, kullanici) {
  localStorage.setItem(ANAHTAR_JETON, jeton);
  localStorage.setItem(ANAHTAR_KULLANICI, JSON.stringify(kullanici));
}
function oturumTemizle() {
  try {
    localStorage.removeItem(ANAHTAR_JETON);
    localStorage.removeItem(ANAHTAR_KULLANICI);
  } catch (h) {
    /* yoksay */
  }
}

// API çağrısı
// Başarılıysa JSON döner. Başarısızsa API'nin "hata" alanındaki Türkçe mesajla Error fırlatır.
async function api(yol, { metod = "GET", govde = null } = {}) {
  const basliklar = { Accept: "application/json" };
  const jeton = jetonAl();
  if (jeton) basliklar.Authorization = "Bearer " + jeton;
  if (govde !== null) basliklar["Content-Type"] = "application/json";

  let yanit;
  try {
    yanit = await fetch("/api" + yol, {
      method: metod,
      headers: basliklar,
      body: govde !== null ? JSON.stringify(govde) : undefined,
    });
  } catch (h) {
    throw new Error("Sunucuya ulaşılamadı. Bağlantınızı kontrol edin.");
  }

  let veri = null;
  try {
    veri = await yanit.json();
  } catch (h) {
    /* JSON değil */
  }

  if (yanit.status === 401 && yol !== "/giris") {
    oturumTemizle();
    location.href = "/index.html";
    throw new Error("Oturum süresi doldu, lütfen yeniden giriş yapın.");
  }
  if (!yanit.ok) {
    throw new Error(
      (veri && veri.hata) ||
        "İstek başarısız oldu (HTTP " + yanit.status + ").",
    );
  }
  return veri;
}

// DOM kurma yardımcısı (metinler güvenli eklenir, XSS olmaz)
// el('p', { sinif: 'soluk' }, 'merhaba', el('b', {}, 'dünya'))
function el(etiket, ozellikler, ...cocuklar) {
  const e = document.createElement(etiket);
  for (const [ad, deger] of Object.entries(ozellikler || {})) {
    if (ad === "sinif") e.className = deger;
    else if (ad.startsWith("on")) e.addEventListener(ad.slice(2), deger);
    else if (deger === true) e.setAttribute(ad, "");
    else if (deger !== false && deger != null) e.setAttribute(ad, deger);
  }
  for (const c of cocuklar.flat()) {
    if (c === null || c === undefined || c === false) continue;
    e.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return e;
}

// biçimlendirme
const PARA_BICIMI = new Intl.NumberFormat("tr-TR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
function para(sayi) {
  return PARA_BICIMI.format(Number(sayi)) + " ₺";
}

function tarihNesnesi(iso) {
  return new Date(iso.slice(0, 10) + "T00:00:00");
}
function gunYaz(iso) {
  return tarihNesnesi(iso).toLocaleDateString("tr-TR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
function kisaGunYaz(iso) {
  return tarihNesnesi(iso).toLocaleDateString("tr-TR", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}
function saatYaz(iso) {
  return iso.slice(11, 16);
}
function zamanYaz(iso) {
  return kisaGunYaz(iso) + " " + saatYaz(iso);
}

const DURUM_ETIKET = {
  aktif: "Aktif",
  kullanildi: "Kullanıldı",
  iptal: "İptal",
};
const DURUM_SINIF = {
  aktif: "rozet-yesil",
  kullanildi: "",
  iptal: "rozet-hata",
};
function durumRozeti(durum) {
  return el(
    "span",
    { sinif: "rozet " + (DURUM_SINIF[durum] || "") },
    DURUM_ETIKET[durum] || durum,
  );
}

// bildirim kutusu
function bildir(kutu, mesaj, tur) {
  const basari = tur === "basari";
  kutu.className = "bildirim " + (basari ? "bildirim-basari" : "bildirim-hata");
  kutu.setAttribute("role", basari ? "status" : "alert");
  kutu.textContent = mesaj;
  kutu.hidden = false;
}
function bildirimiGizle(kutu) {
  kutu.hidden = true;
  kutu.textContent = "";
}

// sayfa başlatma: giriş denetimi + üst çubuk
const SAYFALAR = [
  ["menu.html", "Günün menüsü"],
  ["haftalik.html", "Haftalık menü"],
  ["rezervasyonlarim.html", "Rezervasyonlarım"],
  ["bakiye.html", "Bakiye"],
  ["profil.html", "Profil"],
  ["degerlendirme.html", "Değerlendirme"],
];
const ROL_ETIKET = {
  ogrenci: "Öğrenci",
  personel: "Personel",
  yonetici: "Yönetici",
};

// Giriş yoksa giriş sayfasına yollar ve null döner. Yöneticiye özel sayfada rol yanlışsa menüye yollar.
function sayfaBaslat(aktifSayfa, { yonetici = false } = {}) {
  const kullanici = kullaniciAl();
  if (!jetonAl() || !kullanici) {
    location.replace("/index.html");
    return null;
  }
  if (yonetici && kullanici.rol !== "yonetici") {
    location.replace("/menu.html");
    return null;
  }

  const sayfalar = SAYFALAR.slice();
  if (kullanici.rol === "yonetici")
    sayfalar.push(["yonetici.html", "Yönetici paneli"]);

  const ust = document.getElementById("ust");
  ust.className = "ust-serit";
  ust.replaceChildren(
    el(
      "div",
      { sinif: "kapsayici ust-ic" },
      el("a", { sinif: "marka", href: "/menu.html" }, "🍽 Yemekhane"),
      el(
        "span",
        { sinif: "kullanici-adi" },
        kullanici.ad + " " + kullanici.soyad,
        " · ",
        ROL_ETIKET[kullanici.rol] || kullanici.rol,
      ),
      el(
        "button",
        {
          type: "button",
          sinif: "dugme dugme-ikincil",
          id: "cikis-dugmesi",
          onclick: cikisYap,
        },
        "Çıkış",
      ),
    ),
    el(
      "nav",
      { sinif: "kapsayici gezinme", "aria-label": "Ana gezinme" },
      sayfalar.map(([adres, ad]) =>
        el(
          "a",
          {
            href: "/" + adres,
            "aria-current": adres === aktifSayfa ? "page" : false,
          },
          ad,
        ),
      ),
    ),
  );
  return kullanici;
}

async function cikisYap() {
  try {
    await api("/cikis", { metod: "POST" });
  } catch (h) {
    /* oturum zaten bitmiş olabilir */
  }
  oturumTemizle();
  location.href = "/index.html";
}
