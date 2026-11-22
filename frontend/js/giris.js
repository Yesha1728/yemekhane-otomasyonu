"use strict";
/* GİRİŞ SAYFASI */

const kutu = document.getElementById("bildirim");
const form = document.getElementById("giris-formu");
const dugme = document.getElementById("giris-dugmesi");

// Geçerli bir oturum varsa doğrudan menüye geçebilisniz.
(async function oturumVarMi() {
  if (!jetonAl()) return;
  try {
    await api("/ben");
    location.replace("/menu.html");
  } catch (h) {
    oturumTemizle();
  }
})();

form.addEventListener("submit", async (olay) => {
  olay.preventDefault();
  bildirimiGizle(kutu);
  dugme.disabled = true;
  try {
    const sonuc = await api("/giris", {
      metod: "POST",
      govde: {
        eposta: document.getElementById("eposta").value,
        sifre: document.getElementById("sifre").value,
      },
    });
    oturumKaydet(sonuc.jeton, sonuc.kullanici);
    location.href = "/menu.html";
  } catch (h) {
    bildir(kutu, h.message, "hata"); // E-posta veya şifre yanlış olabilir. O yuzden hata mesajını kullanıcıya gösteriyoruz.
    dugme.disabled = false;
  }
});
