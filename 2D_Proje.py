import pygame
import math
import random

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
BINA_RENGI = (100, 100, 110)
BINA_CATI = (80, 80, 90)
FAR_ISIGI = (255, 255, 200, 100)
PARK_ZEMINI = (70, 70, 80) # Otopark için biraz farklı bir gri

# --- YARDIMCI SINIFLAR ---

class Pusula:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, EKRAN_GENISLIK, 50) # Boyutlandırma (x,y, uzunluk, yükseklik)
        self.font_buyuk = pygame.font.SysFont("Arial", 20, bold=True) # Ana yönler (K, G, D, B)
        self.font_kucuk = pygame.font.SysFont("Arial", 12) # Ara Yönler (KB, KD, GB, GD)
        self.yonler = [
            (0, "D"), (45, "KD"), (90, "K"), (135, "KB"),
            (180, "B"), (225, "GB"), (270, "G"), (315, "GD")
        ]
        
    def ciz(self, ekran, araba_acisi):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA) # SRCALPHA yarı saydam arka yüz oluşturur
        s.fill(PUSULA_ARKA)
        ekran.blit(s, (0, 0))
        
                  #   Pusulanın ibresi
        center_x = EKRAN_GENISLIK // 2
        pygame.draw.polygon(ekran, PUSULA_ISARET, [
            (center_x, 55), (center_x - 10, 40), (center_x + 10, 40)
        ])
        
        fov = 120
        pixels_per_degree = EKRAN_GENISLIK / fov
                # Görüş açısı hesaplama
        current_angle = araba_acisi % 360
        start_angle = int(current_angle - (fov / 2))
        end_angle = int(current_angle + (fov / 2))
        
        for i in range(start_angle, end_angle + 1):
            norm_angle = i % 360
            offset = (i - current_angle) * pixels_per_degree
            pos_x = center_x - offset   # Bu pusulanın arabayla dönmesini sağlar gerçekçilik hissiyatını artırır
            
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
                # Direksiyon halkaları
        pygame.draw.circle(ekran, (30, 30, 30), (x, y), self.yaricap) 
        pygame.draw.circle(ekran, (200, 200, 200), (x, y), self.yaricap, 8) 
        rad = math.radians(-aci)
        kollar = [150, 270, 30]
        for k in kollar:
    # Ana dönme açısı (rad) + Kolun kendi açısı (k)
            k_rad = rad + math.radians(k)
    
    # Trigonometri: Merkezden çembere giden noktanın X ve Y'sini bulma
            end_x = x + math.cos(k_rad) * (self.yaricap - 5)
            end_y = y + math.sin(k_rad) * (self.yaricap - 5)
    
    # Merkezden hesaplanan noktaya çizgi çekme
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
        super().__init__()      # Pygame Sprite özelliklerini yükler
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
            #   Gövde
        pygame.draw.rect(self.original_surface, renk, (2, 2, self.uzunluk-4, self.genislik-4), border_radius=10)
            #   Ön Camlar
        pygame.draw.rect(self.original_surface, (30, 30, 40), (self.uzunluk*0.6, 10, self.uzunluk*0.15, self.genislik-20))
        pygame.draw.rect(self.original_surface, (30, 30, 40), (self.uzunluk*0.2, 10, self.uzunluk*0.25, self.genislik-20))
            #   Konumlandırma
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
        
        self.max_hiz = 18.0       
        self.max_geri_hiz = 6.0   
        self.ivme = 0.5           
        
        self.govde_rengi = KIRMIZI_ARABA
        
        self.pozisyon = pygame.math.Vector2(x, y)
        self.hiz = 0
        self.aci = 0
        self.surtunme = 0.05
        self.donus_hizi = 3.0
        self.direksiyon_acisi = 0 
        self.direksiyon_toplama_hizi = 5
        self.fren_basili = False

        self.olustur_gorsel()

    def olustur_gorsel(self):
        # --- GÖVDE YÜZEYİ (Tekerlekler HARİÇ) ---
        self.govde_surface = pygame.Surface((self.uzunluk, self.genislik), pygame.SRCALPHA)
        # Ana gövde
        pygame.draw.rect(self.govde_surface, self.govde_rengi, (0, 0, self.uzunluk, self.genislik), border_radius=20)
        
        # Camlar ve Detaylar
        pygame.draw.polygon(self.govde_surface, (20, 20, 30), [
            (self.uzunluk * 0.7, 10), (self.uzunluk * 0.7, self.genislik - 10),
            (self.uzunluk * 0.55, self.genislik - 15), (self.uzunluk * 0.55, 15)
        ])
        pygame.draw.rect(self.govde_surface, (20, 20, 30), (self.uzunluk * 0.1, 15, self.uzunluk * 0.2, self.genislik - 30))
        
        # Sürücü kaskı detayı
        pygame.draw.circle(self.govde_surface, self.govde_rengi, (int(self.uzunluk*0.65), 0), 10)
        pygame.draw.circle(self.govde_surface, self.govde_rengi, (int(self.uzunluk*0.65), self.genislik), 10)

        # --- TEKERLEK POZİSYON HESAPLAMALARI ---
        w_len, w_wid = int(self.uzunluk*0.22), int(self.genislik*0.28)
        self.teker_boyut = (w_len, w_wid)
        
        # Arka tekerleklerin sol-üst köşe koordinatları (sabit)
        self.arka_teker_pos = [
            (int(self.uzunluk*0.10), -5), 
            (int(self.uzunluk*0.10), self.genislik-w_wid+5)
        ]
        # Ön tekerleklerin MERKEZ koordinatları (dönecekleri için)
        self.on_teker_merkezler = [
             (int(self.uzunluk*0.80), int(w_wid/2) - 5),
             (int(self.uzunluk*0.80), self.genislik - int(w_wid/2) + 5)
        ]

        # Hitbox için geçici görsel (en son ciz fonksiyonunda güncellenecek)
        self.image = pygame.Surface((self.uzunluk, self.genislik))
        self.image.fill(self.govde_rengi)
        self.rect = self.image.get_rect(center=self.pozisyon)

    def kontrol(self):
        tuslar = pygame.key.get_pressed()
        self.fren_basili = False
        
        # Gaz / Fren Kontrolü
        if tuslar[pygame.K_UP]: 
            if self.hiz < self.max_hiz: self.hiz += self.ivme
        elif tuslar[pygame.K_DOWN]: 
            self.fren_basili = True
            if self.hiz > -self.max_geri_hiz: self.hiz -= self.ivme
        else:
            # Sürtünme ile yavaşlama
            if self.hiz > 0: self.hiz -= self.surtunme
            if self.hiz < 0: self.hiz += self.surtunme
            if abs(self.hiz) < self.surtunme: self.hiz = 0

        # Direksiyon Kontrolü
        hedef_direksiyon = 0
        if tuslar[pygame.K_LEFT]: hedef_direksiyon = 45 
        elif tuslar[pygame.K_RIGHT]: hedef_direksiyon = -45 

        # Direksiyonun yumuşak dönüşü (smooth steering)
        if self.direksiyon_acisi < hedef_direksiyon:
            self.direksiyon_acisi += self.direksiyon_toplama_hizi
        elif self.direksiyon_acisi > hedef_direksiyon:
            self.direksiyon_acisi -= self.direksiyon_toplama_hizi
        
        # Açıyı sınırla (-45 ile +45 derece arası)
        self.direksiyon_acisi = max(-45, min(45, self.direksiyon_acisi))

        # Aracı Döndür (Sadece araç hareket halindeyse)
        if abs(self.hiz) > 0.1:
            yon = 1 if self.hiz > 0 else -1
            # Direksiyon açısına bağlı olarak dönüş hızı çarpanı
            donus_carpani = self.direksiyon_acisi / 45.0 
            self.aci += (self.donus_hizi * donus_carpani * yon)

    def update(self):
        self.kontrol()
        # Yeni pozisyonu hesapla
        radyan = math.radians(self.aci)
        self.pozisyon.x += math.cos(radyan) * self.hiz
        self.pozisyon.y -= math.sin(radyan) * self.hiz
        
        # Harita Sınırları Kontrolü
        if self.pozisyon.x < 150: 
            self.pozisyon.x = 150
            self.hiz = 0
        if self.pozisyon.x > HARITA_GENISLIK - 150: 
            self.pozisyon.x = HARITA_GENISLIK - 150
            self.hiz = 0
        if self.pozisyon.y < 150: 
            self.pozisyon.y = 150
            self.hiz = 0
        if self.pozisyon.y > HARITA_YUKSEKLIK - 150: 
            self.pozisyon.y = HARITA_YUKSEKLIK - 150
            self.hiz = 0

        # Çarpışma (Hitbox) için görseli güncelle
        # Bu sadece çarpışma maskesi için basit bir dikdörtgen tutar.
        self.image = pygame.transform.rotate(self.govde_surface, self.aci)
        self.rect = self.image.get_rect(center=self.pozisyon)

    def ciz(self, ekran, scale_factor, offset_x, offset_y):
        # Ölçeklenmiş boyutlar
        new_w = int(self.uzunluk * scale_factor)
        new_h = int(self.genislik * scale_factor)
        
        # 1. Geçici bir yüzey oluştur (Arabanın tamamı buraya çizilecek)
        temp_surf = pygame.Surface((new_w, new_h), pygame.SRCALPHA)
        
        # 2. Önce GÖVDEYİ çiz (Tekerlekler gövdenin üstünde/yanında görünsün diye)
        scaled_body = pygame.transform.scale(self.govde_surface, (new_w, new_h))
        temp_surf.blit(scaled_body, (0,0))

        # Tekerlek boyutlarını ölçekle
        scaled_w_len = int(self.teker_boyut[0] * scale_factor)
        scaled_w_wid = int(self.teker_boyut[1] * scale_factor)
        
        # --- TEKERLEK GÖRSELİ OLUŞTURMA ---
        # Tasarıma uygun, sade bir tekerlek görseli hazırlayalım.
        wheel_base_surf = pygame.Surface((scaled_w_len, scaled_w_wid), pygame.SRCALPHA)
        # Koyu renk ana lastik (hafif yuvarlatılmış köşeler)
        pygame.draw.rect(wheel_base_surf, TEKERLEK_RENGI, (0, 0, scaled_w_len, scaled_w_wid), border_radius=max(1, int(3*scale_factor)))
        # Dönüşün belli olması için ortasına çok hafif daha açık bir gri çizgi (jant/aks detayı)
        # Bu, aracın sade tasarımını bozmadan dönüş hissi verir.
        line_thickness = max(1, int(2 * scale_factor))
        pygame.draw.line(wheel_base_surf, (50, 50, 60), (0, scaled_w_wid//2), (scaled_w_len, scaled_w_wid//2), line_thickness)

        # 3. ARKA TEKERLEKLERİ Çiz (Sabit)
        for tx, ty in self.arka_teker_pos:
            stx, sty = int(tx * scale_factor), int(ty * scale_factor)
            # Arka tekerlekleri hesaplanan sol-üst pozisyonlarına yerleştir
            temp_surf.blit(wheel_base_surf, (stx, sty))
            
        # 4. ÖN TEKERLEKLERİ Çiz (Dönen)
        # Tekerlek görselini direksiyon açısına göre döndür
        rotated_front_wheel = pygame.transform.rotate(wheel_base_surf, self.direksiyon_acisi)
        
        for mx, my in self.on_teker_merkezler:
            smx, smy = int(mx * scale_factor), int(my * scale_factor)
            # Döndürülmüş görselin merkezini, hesaplanan merkez noktasına oturt
            w_rect = rotated_front_wheel.get_rect(center=(smx, smy))
            temp_surf.blit(rotated_front_wheel, w_rect)
            
        # 5. FARLAR ve STOP LAMBALARI
        lamba_renk = (255, 0, 0) if self.fren_basili else (100, 0, 0)
        pygame.draw.rect(temp_surf, lamba_renk, (0, int(new_h*0.1), int(new_w*0.05), int(new_h*0.2)))
        pygame.draw.rect(temp_surf, lamba_renk, (0, int(new_h*0.7), int(new_w*0.05), int(new_h*0.2)))
        
        # Far Işığı Efekti (Blend Mode ile)
        light_len = 600 * scale_factor
        light_width = 300 * scale_factor
        light_surf = pygame.Surface((light_len, light_width*2), pygame.SRCALPHA)
        points = [(0, light_width/2), (light_len, 0), (light_len, light_width)]
        pygame.draw.polygon(light_surf, FAR_ISIGI, points)
        light_surf_right = pygame.Surface((light_len, light_width*2), pygame.SRCALPHA)
        points_r = [(0, light_width/2), (light_len, 0), (light_len, light_width)]
        pygame.draw.polygon(light_surf_right, FAR_ISIGI, points_r)
        
        temp_surf.blit(light_surf, (new_w * 0.9, new_h * 0.1 - light_width/2), special_flags=pygame.BLEND_ADD)
        temp_surf.blit(light_surf_right, (new_w * 0.9, new_h * 0.9 - light_width/2), special_flags=pygame.BLEND_ADD)

        # 6. SON ADIM: Tüm arabayı harita üzerindeki açısına göre döndür ve ekrana bas
        final_rotated = pygame.transform.rotate(temp_surf, self.aci)
        screen_x = (self.pozisyon.x * scale_factor) + offset_x
        screen_y = (self.pozisyon.y * scale_factor) + offset_y
        rect = final_rotated.get_rect(center=(screen_x, screen_y))
        ekran.blit(final_rotated, rect)

class ArabaSimulasyonu:
    def __init__(self):
        pygame.init()
        self.ekran = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        pygame.display.set_caption("2D Simülasyon")
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
        
        print("Harita işleniyor (Yollar ve Binalar)...")
        self.gorunur_harita = pygame.transform.smoothscale(
            self.pist_yuzeyi_high_res, 
            (int(scaled_map_w), int(scaled_map_h))
        )
        
        self.pusula = Pusula()
        self.direksiyon_ui = DireksiyonGostergesi()
        
        self.araba = Araba(250, 1650)
        
        self.duvar_maskesi = pygame.mask.from_surface(self.maske_yuzeyi)

    def dashed_line(self, surface, color, start_pos, end_pos, width=5, dash_len=50, gap_len=30):
        start_vec = pygame.math.Vector2(start_pos)
        end_vec = pygame.math.Vector2(end_pos)
        distance = start_vec.distance_to(end_vec)
        direction = (end_vec - start_vec).normalize()
        
        current_dist = 0
        while current_dist < distance:
            start_point = start_vec + direction * current_dist
            end_point = start_point + direction * min(dash_len, distance - current_dist)
            pygame.draw.line(surface, color, start_point, end_point, width)
            current_dist += dash_len + gap_len

    def ada_ciz(self, x, y, w, h, yuvarlaklik=50, bina_yap=True):
        pygame.draw.rect(self.pist_yuzeyi_high_res, (100, 100, 100), (x-5, y-5, w+10, h+10), border_radius=yuvarlaklik) 
        pygame.draw.rect(self.pist_yuzeyi_high_res, YESIL_CIM, (x, y, w, h), border_radius=yuvarlaklik) 
        pygame.draw.rect(self.maske_yuzeyi, (0,0,0,255), (x, y, w, h), border_radius=yuvarlaklik)
        if bina_yap:
            self.bina_doldur(x + 50, y + 50, w - 100, h - 100)

    def bina_doldur(self, area_x, area_y, area_w, area_h):
        bina_boyutu = 350
        bosluk = 50
        cols = int(area_w / (bina_boyutu + bosluk))
        rows = int(area_h / (bina_boyutu + bosluk))
        
        for r in range(rows):
            for c in range(cols):
                bx = area_x + c * (bina_boyutu + bosluk)
                by = area_y + r * (bina_boyutu + bosluk)
                if random.random() > 0.8:
                    pygame.draw.circle(self.pist_yuzeyi_high_res, (20, 80, 20), (int(bx+bina_boyutu/2), int(by+bina_boyutu/2)), 100)
                    continue
                pygame.draw.rect(self.pist_yuzeyi_high_res, (50, 50, 50), (bx+10, by+10, bina_boyutu, bina_boyutu))
                pygame.draw.rect(self.pist_yuzeyi_high_res, BINA_RENGI, (bx, by, bina_boyutu, bina_boyutu))
                pygame.draw.rect(self.pist_yuzeyi_high_res, BINA_CATI, (bx+20, by+20, bina_boyutu-40, bina_boyutu-40))
                pygame.draw.rect(self.maske_yuzeyi, (0,0,0,255), (bx, by, bina_boyutu, bina_boyutu))

    def park_cizgisi_cek(self, x, y, w, h, tip="dikey"):
        pygame.draw.rect(self.pist_yuzeyi_high_res, PARK_ZEMINI, (x, y, w, h)) 
        pygame.draw.rect(self.pist_yuzeyi_high_res, SARI_CIZGI, (x, y, w, h), 20) 
        if tip == "dikey": 
            bosluk = h / 2 
            self.dashed_line(self.pist_yuzeyi_high_res, SARI_CIZGI, (x, y + bosluk), (x + w, y + bosluk), width=3)

    def baba_ekle(self, x, y):
        self.dubalar.add(Baba(x, y))

    def park_araci_ekle(self, x, y, aci=90, renk=(100, 100, 100)):
        arac = ParkHalindekiAraba(x, y, aci, renk)
        self.park_araclari.add(arac)

    def harita_olustur(self):
        self.pist_yuzeyi_high_res.fill(GRI_YOL)
        self.maske_yuzeyi.fill((0,0,0,0)) 

        # --- YOL ŞERİTLERİNİ ÇİZ (Adalardan Önce) ---
        # Üst Yatay Yol
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (150, 250), (7500, 250))
        # Orta Yatay Yol
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (150, 2250), (7500, 2250))
        # Alt Yatay Yol (Kavşağa kadar)
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (150, 4750), (7500, 4750))
        # Dikey Bağlantılar
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (1750, 500), (1750, 6250))
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (3850, 500), (3850, 2250))
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (3850, 2250), (3850, 6250))
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (4650, 500), (4650, 2250))
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (4650, 2250), (4650, 6250))

        # Sondaki '5' çizginin kalınlığıdır. İsteğine göre artırıp azaltabilirsin.
        pygame.draw.line(self.pist_yuzeyi_high_res, BEYAZ, (7500, 250), (7500, 6250), 50)
        pygame.draw.line(self.pist_yuzeyi_high_res, BEYAZ, (4250, 250), (4250, 6250), 5)

        # Adaları ve Binaları Çiz
        self.ada_ciz(500, 500, 1000, 1450) 
        self.ada_ciz(2000, 500, 1500, 1450)
        self.ada_ciz(5000, 500, 2000, 1450)
        self.ada_ciz(500, 2500, 1000, 2000)
        self.ada_ciz(500, 5000, 1000, 1300) 

        # Yol Çizgileri (Adaların üzerindeki beyaz çizgiler)
        D_yolu = [(5000, 2500), (7000, 2500), (7000, 4500), (5500, 4500), (5000, 4000)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , D_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, D_yolu, width=5)
        pygame.draw.polygon(self.maske_yuzeyi, (0,0,0,255), D_yolu)

        E_yolu = [(2000, 2500), (3500, 2500), (3500, 4000), (3000, 4500), (2000, 4500)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , E_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, E_yolu, width=5)
        pygame.draw.polygon(self.maske_yuzeyi, (0,0,0,255), E_yolu)

        F_yolu = [(2000, 5000), (3000, 5000), (3500, 5500), (3500, 6300), (2000, 6300)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , F_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, F_yolu, width=5)
        pygame.draw.polygon(self.maske_yuzeyi, (0,0,0,255), F_yolu)

        G_yolu = [(5500, 5000), (7000, 5000), (7000, 6300), (5000, 6300), (5000, 5500)]
        pygame.draw.polygon(self.pist_yuzeyi_high_res, YESIL_CIM , G_yolu)
        pygame.draw.polygon(self.pist_yuzeyi_high_res, BEYAZ, G_yolu, width=5)
        pygame.draw.polygon(self.maske_yuzeyi, (0,0,0,255), G_yolu)

        # Dönel Kavşak
        g_x, g_y = 4250, 4800 
        g_r = 300
        pygame.draw.circle(self.pist_yuzeyi_high_res, (200, 200, 200), (g_x, g_y), g_r + 5) 
        pygame.draw.circle(self.pist_yuzeyi_high_res, YESIL_CIM, (g_x, g_y), g_r) 
        pygame.draw.rect(self.pist_yuzeyi_high_res, (80, 80, 80), (g_x-50, g_y-50, 100, 100))
        pygame.draw.circle(self.maske_yuzeyi, (0,0,0,255), (g_x, g_y), g_r) 

        # --- GÜZELLEŞTİRİLMİŞ L-PARK ALANI ---
        l_x, l_y = 500, 1500
        l_w, l_h = 500, 320 
        # Zemini boya
        pygame.draw.rect(self.pist_yuzeyi_high_res, PARK_ZEMINI, (l_x, l_y, l_w, l_h))
        # Giriş yolu çizgileri (Beyaz kesik)
        self.dashed_line(self.pist_yuzeyi_high_res, BEYAZ, (l_x, l_y + l_h/2), (l_x + l_w - 150, l_y + l_h/2), width=3, dash_len=30, gap_len=20)
        # Park yeri kutusu (Sarı düz)
        park_kutusu_x = l_x + l_w - 150
        park_kutusu_y = l_y + 50
        park_kutusu_h = l_h - 100
        pygame.draw.rect(self.pist_yuzeyi_high_res, SARI_CIZGI, (park_kutusu_x, park_kutusu_y, 150, park_kutusu_h), 5)
        
        # Maskeden temizle (parka girebilsin)
        pygame.draw.rect(self.maske_yuzeyi, (0,0,0,0), (l_x, l_y, l_w, l_h))
        
        for i in range(5):
            self.baba_ekle(l_x + (i*100), l_y - 20) 
            self.baba_ekle(l_x + (i*100), l_y + l_h + 20) 

        # Sağdaki Paralel Park Alanları
        self.park_cizgisi_cek(8000, 1000, 320, 1000, tip="dikey")
        self.park_cizgisi_cek(8000, 2000, 320, 1000, tip="dikey")
        self.park_cizgisi_cek(8000, 3000, 320, 1000, tip="dikey")
        self.park_cizgisi_cek(8000, 4000, 320, 1000, tip="dikey")
        self.park_cizgisi_cek(8000, 5000, 320, 1000, tip="dikey")

        self.park_araci_ekle(8155, 1250, aci=90, renk=(50, 150, 50))
        self.park_araci_ekle(8155, 4250, aci=90, renk=(50, 50, 255))
        self.park_araci_ekle(8160, 1700, aci=90, renk=(50, 50, 180))
        self.park_araci_ekle(8160, 2700, aci=90, renk=(180, 50, 50))
        self.park_araci_ekle(8160, 4700, aci=90, renk=(100, 100, 100))
        self.park_araci_ekle(1000, 2400, aci=0, renk=(50, 150, 50))
        
        # --- HARİTA SINIRLARI (BEYAZ ÇERÇEVE) ---
        pygame.draw.rect(self.pist_yuzeyi_high_res, BEYAZ, (0, 0, HARITA_GENISLIK, HARITA_YUKSEKLIK), 10)

    def calistir(self):
        calisiyor = True
        font = pygame.font.SysFont("Arial", 18, bold=True)

        while calisiyor:
            dt = self.saat.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: calisiyor = False

            self.araba.update()

            offset = (int(self.araba.rect.x), int(self.araba.rect.y))
            try:
                kaza_duvar = self.duvar_maskesi.overlap(pygame.mask.from_surface(self.araba.image), offset)
            except:
                kaza_duvar = False
            
            kaza_duba = pygame.sprite.spritecollide(self.araba, self.dubalar, False, pygame.sprite.collide_mask)
            kaza_park = pygame.sprite.spritecollide(self.araba, self.park_araclari, False, pygame.sprite.collide_mask)

            if kaza_duvar or kaza_duba or kaza_park:
                self.araba.hiz *= -0.5 
                self.araba.pozisyon.x -= math.cos(math.radians(self.araba.aci)) * 10
                self.araba.pozisyon.y += math.sin(math.radians(self.araba.aci)) * 10

            self.ekran.fill(SIYAH)
            
            self.ekran.blit(self.gorunur_harita, (self.offset_x, self.offset_y))
            
            for duba in self.dubalar:
                duba.ciz(self.ekran, self.scale, self.offset_x, self.offset_y)
            for p_arac in self.park_araclari:
                p_arac.ciz(self.ekran, self.scale, self.offset_x, self.offset_y)
            
            self.araba.ciz(self.ekran, self.scale, self.offset_x, self.offset_y)

            pygame.draw.rect(self.ekran, (0,0,0), (10, 10, 200, 60), border_radius=10)
            pygame.draw.rect(self.ekran, BEYAZ, (10, 10, 200, 60), 2, border_radius=10)
            hiz_yazi = font.render(f"HIZ: {abs(self.araba.hiz*3.6):.1f} km/s", True, BEYAZ)
            konum_yazi = font.render(f"X: {int(self.araba.pozisyon.x)} Y: {int(self.araba.pozisyon.y)}", True, BEYAZ)
            self.ekran.blit(hiz_yazi, (20, 20))
            self.ekran.blit(konum_yazi, (20, 45))

            self.pusula.ciz(self.ekran, self.araba.aci)
            self.direksiyon_ui.ciz(self.ekran, self.araba.direksiyon_acisi)

            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    ArabaSimulasyonu().calistir()
