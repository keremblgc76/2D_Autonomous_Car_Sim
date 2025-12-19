import pygame
import math

# --- AYARLAR ---
EKRAN_GENISLIK, EKRAN_YUKSEKLIK = 1600, 900 
FPS = 60

# --- HARİTA AYARLARI ---
HARITA_GENISLIK = 8500  
HARITA_YUKSEKLIK = 6500 

# --- RENKLER ---
SIYAH = (0, 0, 0)
BEYAZ = (240, 240, 240)
GRI_YOL = (60, 60, 60)
YESIL_CIM = (34, 100, 34)
SARI_CIZGI = (255, 215, 0)
KIRMIZI_ARABA = (220, 20, 60)
TURUNCU_BABA = (255, 69, 0)
TEKERLEK_RENGI = (20, 20, 20)
PUSULA_ARKA = (0, 0, 0, 150)
PUSULA_YAZI = (255, 255, 255)
PUSULA_ISARET = (255, 215, 0)

# --- YARDIMCI SINIFLAR ---

class Pusula:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, EKRAN_GENISLIK, 50)
        self.font_buyuk = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_kucuk = pygame.font.SysFont("Arial", 12)
        self.yonler = [
            (0, "D"), (45, "KD"), (90, "K"), (135, "KB"),
            (180, "B"), (225, "GB"), (270, "G"), (315, "GD")
        ]
        
    def ciz(self, ekran, araba_acisi):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(PUSULA_ARKA)
        ekran.blit(s, (0, 0))
        
        center_x = EKRAN_GENISLIK // 2
        pygame.draw.polygon(ekran, PUSULA_ISARET, [
            (center_x, 55), (center_x - 10, 40), (center_x + 10, 40)
        ])
        
        fov = 120
        pixels_per_degree = EKRAN_GENISLIK / fov
        current_angle = araba_acisi % 360
        start_angle = int(current_angle - (fov / 2))
        end_angle = int(current_angle + (fov / 2))
        
        for i in range(start_angle, end_angle + 1):
            norm_angle = i % 360
            offset = (i - current_angle) * pixels_per_degree
            pos_x = center_x - offset
            
            if pos_x < -50 or pos_x > EKRAN_GENISLIK + 50: continue
                
            match_found = False
            for aci, isim in self.yonler:
                if aci == norm_angle:
                    if len(isim) == 1:
                        text = self.font_buyuk.render(isim, True, PUSULA_YAZI)
                        pygame.draw.line(ekran, BEYAZ, (pos_x, 30), (pos_x, 45), 2)
                    else:
                        text = self.font_kucuk.render(isim, True, (200, 200, 200))
                        pygame.draw.line(ekran, (200, 200, 200), (pos_x, 35), (pos_x, 45), 1)
                    text_rect = text.get_rect(center=(pos_x, 20))
                    ekran.blit(text, text_rect)
                    match_found = True
                    break
            
            if not match_found and i % 15 == 0:
                pygame.draw.line(ekran, (150, 150, 150), (pos_x, 40), (pos_x, 45), 1)
                if i % 30 == 0:
                     num_text = self.font_kucuk.render(str(norm_angle), True, (100, 100, 100))
                     num_rect = num_text.get_rect(center=(pos_x, 20))
                     ekran.blit(num_text, num_rect)

class DireksiyonGostergesi:
    def __init__(self):
        self.yaricap = 60
        self.merkez = (100, EKRAN_YUKSEKLIK - 100)
        self.font = pygame.font.SysFont("Consolas", 16, bold=True)

    def ciz(self, ekran, aci):
        x, y = self.merkez
        pygame.draw.circle(ekran, (30, 30, 30), (x, y), self.yaricap) 
        pygame.draw.circle(ekran, (200, 200, 200), (x, y), self.yaricap, 8) 
        rad = math.radians(-aci)
        kollar = [0, 120, 240]
        for k in kollar:
            k_rad = rad + math.radians(k)
            end_x = x + math.cos(k_rad) * (self.yaricap - 5)
            end_y = y + math.sin(k_rad) * (self.yaricap - 5)
            pygame.draw.line(ekran, (150, 150, 150), (x, y), (end_x, end_y), 6)
        pygame.draw.circle(ekran, (50, 50, 50), (x, y), 15)
        pygame.draw.line(ekran, (255, 0, 0), (x, y - self.yaricap - 5), (x, y - self.yaricap + 10), 4)
        text = f"{int(aci)}°"
        text_surf = self.font.render(text, True, BEYAZ)
        text_rect = text_surf.get_rect(center=(x, y + self.yaricap + 25))
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(ekran, (0, 0, 0), bg_rect, border_radius=5)
        ekran.blit(text_surf, text_rect)

# --- ANA SINIFLAR ---

class Baba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.yaricap = 15 
        self.image = pygame.Surface((self.yaricap*2, self.yaricap*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, TURUNCU_BABA, (self.yaricap, self.yaricap), self.yaricap)
        pygame.draw.circle(self.image, BEYAZ, (self.yaricap, self.yaricap), self.yaricap//2, 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.gercek_pos = pygame.math.Vector2(x, y)

    def ciz(self, ekran, scale_factor, offset_x, offset_y):
        yeni_r = max(3, int(self.yaricap * scale_factor)) 
        ekran_x = int(self.gercek_pos.x * scale_factor) + offset_x
        ekran_y = int(self.gercek_pos.y * scale_factor) + offset_y
        pygame.draw.circle(ekran, TURUNCU_BABA, (ekran_x, ekran_y), yeni_r)

class ParkHalindekiAraba(pygame.sprite.Sprite):
    def __init__(self, x, y, aci=90, renk=(100, 100, 150)):
        super().__init__()
        self.uzunluk = 350 
        self.genislik = 150
        self.aci = aci
        self.original_surface = pygame.Surface((self.uzunluk, self.genislik), pygame.SRCALPHA)
        w_len, w_wid = int(self.uzunluk*0.2), int(self.genislik*0.25)
        wheels = [(int(self.uzunluk*0.75), 0), (int(self.uzunluk*0.75), self.genislik-w_wid),
                  (int(self.uzunluk*0.15), 0), (int(self.uzunluk*0.15), self.genislik-w_wid)]
        for wx, wy in wheels:
            pygame.draw.rect(self.original_surface, TEKERLEK_RENGI, (wx, wy, w_len, w_wid))
        pygame.draw.rect(self.original_surface, renk, (2, 2, self.uzunluk-4, self.genislik-4), border_radius=10)
        pygame.draw.rect(self.original_surface, (50, 50, 60), (self.uzunluk*0.6, 5, self.uzunluk*0.2, self.genislik-10))
        self.gercek_pos = pygame.math.Vector2(x, y)
        self.image = pygame.transform.rotate(self.original_surface, self.aci)
        self.rect = self.image.get_rect(center=(x, y))

    def ciz(self, ekran, scale_factor, offset_x, offset_y):
        new_w = int(self.uzunluk * scale_factor)
        new_h = int(self.genislik * scale_factor)
        scaled_img = pygame.transform.scale(self.original_surface, (new_w, new_h))
        rotated_img = pygame.transform.rotate(scaled_img, self.aci)
        screen_x = (self.gercek_pos.x * scale_factor) + offset_x
        screen_y = (self.gercek_pos.y * scale_factor) + offset_y
        rect = rotated_img.get_rect(center=(screen_x, screen_y))
        ekran.blit(rotated_img, rect)

class Araba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.uzunluk = 350 
        self.genislik = 150
        
        # HIZ LİMİTİ AYARLARI
        self.max_hiz = 15.0       # İleri maksimum hız
        self.max_geri_hiz = 5.0   # Geri maksimum hız
        self.ivme = 0.4           # Hızlanma gücü
        
        self.original_surface = pygame.Surface((self.uzunluk, self.genislik), pygame.SRCALPHA)
        w_len, w_wid = int(self.uzunluk*0.2), int(self.genislik*0.25)
        wheels = [(int(self.uzunluk*0.75), 0), (int(self.uzunluk*0.75), self.genislik-w_wid),
                  (int(self.uzunluk*0.15), 0), (int(self.uzunluk*0.15), self.genislik-w_wid)]
        for wx, wy in wheels:
            pygame.draw.rect(self.original_surface, TEKERLEK_RENGI, (wx, wy, w_len, w_wid))
        pygame.draw.rect(self.original_surface, KIRMIZI_ARABA, (2, 2, self.uzunluk-4, self.genislik-4), border_radius=10)
        pygame.draw.rect(self.original_surface, (50, 50, 60), (self.uzunluk*0.6, 5, self.uzunluk*0.2, self.genislik-10))

        self.image = self.original_surface
        self.rect = self.image.get_rect(center=(x, y))
        self.pozisyon = pygame.math.Vector2(x, y)
        self.hiz = 0
        self.aci = 0
        self.surtunme = 0.05
        self.donus_hizi = 2.5
        self.direksiyon_acisi = 0 
        self.direksiyon_toplama_hizi = 5

    def kontrol(self):
        tuslar = pygame.key.get_pressed()
        
        # GAZ / FREN VE HIZ SINIRLAMASI
        if tuslar[pygame.K_UP]: 
            if self.hiz < self.max_hiz: # Hız sınırı kontrolü
                self.hiz += self.ivme
        elif tuslar[pygame.K_DOWN]: 
            if self.hiz > -self.max_geri_hiz: # Geri hız sınırı
                self.hiz -= self.ivme
        else:
            if self.hiz > 0: self.hiz -= self.surtunme
            if self.hiz < 0: self.hiz += self.surtunme
            if abs(self.hiz) < self.surtunme: self.hiz = 0

        # Direksiyon
        hedef_direksiyon = 0
        if tuslar[pygame.K_LEFT]: hedef_direksiyon = 90 
        elif tuslar[pygame.K_RIGHT]: hedef_direksiyon = -90 

        if self.direksiyon_acisi < hedef_direksiyon:
            self.direksiyon_acisi += self.direksiyon_toplama_hizi * 2
        elif self.direksiyon_acisi > hedef_direksiyon:
            self.direksiyon_acisi -= self.direksiyon_toplama_hizi * 2
        
        if self.direksiyon_acisi > 90: self.direksiyon_acisi = 90
        if self.direksiyon_acisi < -90: self.direksiyon_acisi = -90

        if abs(self.hiz) > 0.1:
            yon = 1 if self.hiz > 0 else -1
            donus_carpani = self.direksiyon_acisi / 90.0 
            self.aci += (self.donus_hizi * donus_carpani * yon)

    def update(self):
        self.kontrol()
        radyan = math.radians(self.aci)
        self.pozisyon.x += math.cos(radyan) * self.hiz
        self.pozisyon.y -= math.sin(radyan) * self.hiz
        
        self.rotated_image_phys = pygame.transform.rotate(self.original_surface, self.aci)
        self.rect = self.rotated_image_phys.get_rect(center=self.pozisyon)
        self.image = self.rotated_image_phys 

    def ciz(self, ekran, scale_factor, offset_x, offset_y):
        new_w = int(self.uzunluk * scale_factor)
        new_h = int(self.genislik * scale_factor)
        scaled_img = pygame.transform.scale(self.original_surface, (new_w, new_h))
        rotated_img = pygame.transform.rotate(scaled_img, self.aci)
        screen_x = (self.pozisyon.x * scale_factor) + offset_x
        screen_y = (self.pozisyon.y * scale_factor) + offset_y
        rect = rotated_img.get_rect(center=(screen_x, screen_y))
        ekran.blit(rotated_img, rect)

class ArabaSimulasyonu:
    def __init__(self):
        pygame.init()
        self.ekran = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        pygame.display.set_caption("Sürücü Kursu - Kolay Kontrol Modu")
        self.saat = pygame.time.Clock()
        
        self.pist_yuzeyi_high_res = pygame.Surface((HARITA_GENISLIK, HARITA_YUKSEKLIK))
        self.maske_yuzeyi = pygame.Surface((HARITA_GENISLIK, HARITA_YUKSEKLIK), pygame.SRCALPHA)
        
        self.dubalar = pygame.sprite.Group()
        self.park_araclari = pygame.sprite.Group()
        
        self.harita_olustur()
        
        scale_w = EKRAN_GENISLIK / HARITA_GENISLIK
        scale_h = EKRAN_YUKSEKLIK / HARITA_YUKSEKLIK
        self.scale = min(scale_w, scale_h) * 0.95 
        scaled_map_w = HARITA_GENISLIK * self.scale
        scaled_map_h = HARITA_YUKSEKLIK * self.scale
        self.offset_x = (EKRAN_GENISLIK - scaled_map_w) / 2
        self.offset_y = (EKRAN_YUKSEKLIK - scaled_map_h) / 2
        
        print("Harita işleniyor...")
        self.gorunur_harita = pygame.transform.smoothscale(
            self.pist_yuzeyi_high_res, 
            (int(scaled_map_w), int(scaled_map_h))
        )
        
        self.pusula = Pusula()
        self.direksiyon_ui = DireksiyonGostergesi()
        
        # --- BAŞLANGIÇ NOKTASI GÜNCELLENDİ ---
        # 700 yerine 250 yaptık (Yolun ortası)
        self.araba = Araba(250, 1650)
        
        self.duvar_maskesi = pygame.mask.from_surface(self.maske_yuzeyi)

    def ada_ciz(self, x, y, w, h, yuvarlaklik=50):
        pygame.draw.rect(self.pist_yuzeyi_high_res, (180, 180, 180), (x-5, y-5, w+10, h+10), border_radius=yuvarlaklik) 
        pygame.draw.rect(self.pist_yuzeyi_high_res, YESIL_CIM, (x, y, w, h), border_radius=yuvarlaklik) 
        pygame.draw.rect(self.maske_yuzeyi, (0,0,0,255), (x, y, w, h), border_radius=yuvarlaklik)

    def park_cizgisi_cek(self, x, y, w, h, tip="dikey"):
        pygame.draw.rect(self.pist_yuzeyi_high_res, (80, 80, 80), (x, y, w, h)) 
        pygame.draw.rect(self.pist_yuzeyi_high_res, SARI_CIZGI, (x, y, w, h), 5) 
        if tip == "dikey": 
            bosluk = h / 2 
            pygame.draw.line(self.pist_yuzeyi_high_res, SARI_CIZGI, (x, y + bosluk), (x + w, y + bosluk), 3)

    def baba_ekle(self, x, y):
        self.dubalar.add(Baba(x, y))

    def park_araci_ekle(self, x, y, aci=90, renk=(100, 100, 100)):
        arac = ParkHalindekiAraba(x, y, aci, renk)
        self.park_araclari.add(arac)

    def harita_olustur(self):
        self.pist_yuzeyi_high_res.fill(GRI_YOL)
        self.maske_yuzeyi.fill((0,0,0,0)) 

        self.ada_ciz(500, 500, 1000, 1450) 
        self.ada_ciz(2000, 500, 1500, 1450)
        self.ada_ciz(5000, 500, 2000, 1450)
        self.ada_ciz(500, 2500, 1000, 2000)
        self.ada_ciz(500, 5000, 1000, 1300) 

        D_yolu = [(5000, 2500), (7000, 2500), (7000, 4500), (5500, 4500), (5000, 4000)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , D_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, D_yolu, width=5)

        E_yolu = [(2000, 2500), (3500, 2500), (3500, 4000), (3000, 4500), (2000, 4500)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , E_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, E_yolu, width=5)

        F_yolu = [(2000, 5000), (3000, 5000), (3500, 5500), (3500, 6300), (2000, 6300)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , F_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, F_yolu, width=5)

        G_yolu = [(5500, 5000), (7000, 5000), (7000, 6300), (5000, 6300), (5000, 5500)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , G_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, G_yolu, width=5)

        g_x, g_y = 4250, 4800 
        g_r = 300
        pygame.draw.circle(self.pist_yuzeyi_high_res, (200, 200, 200), (g_x, g_y), g_r + 5) 
        pygame.draw.circle(self.pist_yuzeyi_high_res, YESIL_CIM, (g_x, g_y), g_r) 
        pygame.draw.circle(self.maske_yuzeyi, (0,0,0,255), (g_x, g_y), g_r) 

        # PARK ALANLARI VE DUBALAR
        l_x, l_y = 500, 1500
        l_w, l_h = 500, 320 
        self.park_cizgisi_cek(l_x, l_y, l_w, l_h, tip="yatay")
        
        # --- DÜZELTME: L PARK ALANINI MASKEDEN SİL (GİRİLEBİLİR OLSUN) ---
        pygame.draw.rect(self.maske_yuzeyi, (0,0,0,0), (l_x, l_y, l_w, l_h))
        
        for i in range(5):
            self.baba_ekle(l_x + (i*100), l_y - 20) 
            self.baba_ekle(l_x + (i*100), l_y + l_h + 20) 

        self.park_cizgisi_cek(8000, 1500, 320, 1000, tip="dikey")
        self.park_cizgisi_cek(8000, 2500, 320, 1000, tip="dikey")
        self.park_cizgisi_cek(8000, 3500, 320, 1000, tip="dikey")
        self.park_cizgisi_cek(8000, 4500, 320, 1000, tip="dikey")

        self.park_araci_ekle(8160, 1700, aci=90, renk=(50, 50, 180))
        self.park_araci_ekle(8160, 2800, aci=90, renk=(180, 50, 50))
        self.park_araci_ekle(8160, 4800, aci=90, renk=(100, 100, 100))
        self.park_araci_ekle(1000, 2300, aci=0, renk=(50, 150, 50))

    def calistir(self):
        calisiyor = True
        font = pygame.font.SysFont("Arial", 18, bold=True)

        while calisiyor:
            dt = self.saat.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: calisiyor = False

            # --- FİZİK ---
            self.araba.update()

            # Çarpışma Kontrolleri
            offset = (int(self.araba.rect.x), int(self.araba.rect.y))
            try:
                kaza_duvar = self.duvar_maskesi.overlap(pygame.mask.from_surface(self.araba.image), offset)
            except:
                kaza_duvar = False
            
            kaza_duba = pygame.sprite.spritecollide(self.araba, self.dubalar, False, pygame.sprite.collide_mask)
            kaza_park = pygame.sprite.spritecollide(self.araba, self.park_araclari, False, pygame.sprite.collide_mask)

            if kaza_duvar or kaza_duba or kaza_park:
                self.araba.hiz *= -0.5 

            # --- ÇİZİM ---
            self.ekran.fill(SIYAH)
            
            self.ekran.blit(self.gorunur_harita, (self.offset_x, self.offset_y))
            
            for duba in self.dubalar:
                duba.ciz(self.ekran, self.scale, self.offset_x, self.offset_y)
            for p_arac in self.park_araclari:
                p_arac.ciz(self.ekran, self.scale, self.offset_x, self.offset_y)
            self.araba.ciz(self.ekran, self.scale, self.offset_x, self.offset_y)

            # Bilgi Paneli
            pygame.draw.rect(self.ekran, (0,0,0), (10, 10, 200, 60), border_radius=10)
            pygame.draw.rect(self.ekran, BEYAZ, (10, 10, 200, 60), 2, border_radius=10)
            hiz_yazi = font.render(f"HIZ: {abs(self.araba.hiz*3.6):.1f} km/s", True, BEYAZ)
            konum_yazi = font.render(f"KONUM: {int(self.araba.pozisyon.x)}", True, BEYAZ)
            self.ekran.blit(hiz_yazi, (20, 20))
            self.ekran.blit(konum_yazi, (20, 45))

            self.pusula.ciz(self.ekran, self.araba.aci)
            self.direksiyon_ui.ciz(self.ekran, self.araba.direksiyon_acisi)

            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    ArabaSimulasyonu().calistir()
