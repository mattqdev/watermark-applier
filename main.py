import os
from PIL import Image, ImageStat, ImageOps

def analizza_luminosita(regione):
    """Analizza la luminosità media: 0 è nero, 255 è bianco."""
    stat = ImageStat.Stat(regione.convert('L'))
    return stat.mean[0]

def applica_watermark(
    input_folder, 
    output_folder, 
    watermark_path, 
    ricorsivo=True, 
    width_percent=25, 
    auto_inverte=True,      # Inverte in scuro se lo sfondo è chiaro
    soglia_inversione=170,  # Più alta è, più lo sfondo deve essere bianco per invertire
    opacita_fissa=None      # Se impostato (es. 200), ignora il calcolo auto
):
    if not os.path.exists(input_folder): return
    
    # Carichiamo il watermark BIANCO originale
    wm_original = Image.open(watermark_path).convert("RGBA")
    
    # Prepariamo la versione SCURA per sfondi chiari
    # ImageOps.invert funziona su RGB, poi riapplichiamo l'alpha
    wm_dark = ImageOps.invert(wm_original.convert("RGB")).convert("RGBA")
    wm_dark.putalpha(wm_original.getchannel('A'))

    conteggio = 0
    for root, _, files in os.walk(input_folder):
        if not ricorsivo and root != input_folder: continue

        for filename in files:
            if filename.lower().endswith(".png"):
                path_s = os.path.join(root, filename)
                target_dir = os.path.join(output_folder, os.path.relpath(root, input_folder))
                os.makedirs(target_dir, exist_ok=True)

                try:
                    with Image.open(path_s).convert("RGBA") as img:
                        img_w, img_h = img.size
                        
                        # 1. Ridimensionamento
                        tw = int(img_w * width_percent / 100)
                        th = int(float(wm_original.size[1]) * (tw / float(wm_original.size[0])))
                        
                        # 2. Posizionamento e Analisi Sfondo
                        margin = int(img_w * 0.03) # Margine leggermente più ampio
                        pos = (img_w - tw - margin, img_h - th - margin)
                        regione_sotto = img.crop((pos[0], pos[1], pos[0] + tw, pos[1] + th))
                        lum = analizza_luminosita(regione_sotto)

                        # 3. Logica di Contrasto per Watermark BIANCO
                        # Se lo sfondo è molto CHIARO (> soglia), usiamo il watermark SCURO
                        if auto_inverte and lum > soglia_inversione:
                            wm_lavoro = wm_dark.copy()
                            status = "INVERTITO (SCURO)"
                        else:
                            wm_lavoro = wm_original.copy()
                            status = "ORIGINALE (BIANCO)"

                        wm_lavoro = wm_lavoro.resize((tw, th), Image.Resampling.LANCZOS)

                        # 4. Calcolo Opacità Rigida
                        # Se non è fissa, la rendiamo molto alta per garantire leggibilità
                        if opacita_fissa:
                            livello_op = opacita_fissa
                        else:
                            # Se lo sfondo è "grigio medio" (difficile), forziamo opacità massima
                            if 100 < lum < 200:
                                livello_op = 255
                            else:
                                livello_op = 220

                        alpha = wm_lavoro.getchannel('A')
                        alpha = alpha.point(lambda i: i * (livello_op / 255.0))
                        wm_lavoro.putalpha(alpha)

                        # 5. Applicazione
                        img.paste(wm_lavoro, pos, wm_lavoro)
                        img.save(os.path.join(target_dir, filename), "PNG")
                        
                        print(f"✅ {filename} | Lum: {int(lum)} | Mode: {status} | Op: {livello_op}")
                        conteggio += 1

                except Exception as e:
                    print(f"❌ Errore {filename}: {e}")

    print(f"\nFine. Immagini salvate in: {output_folder}")

# --- ESECUZIONE ---
applica_watermark(
    input_folder="inputs",
    output_folder="output_final",
    watermark_path="Watermark.png",
    ricorsivo=True,
    width_percent=20,       
    auto_inverte=True,      
    soglia_inversione=180,  # Se lo sfondo è sopra 180 (molto chiaro), il watermark diventa nero
    opacita_fissa=None      # Lascia None per l'opacità intelligente
)