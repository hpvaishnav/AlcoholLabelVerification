import os
import csv
from PIL import Image, ImageDraw, ImageFont

def create_directories():
    os.makedirs("sample_data/labels", exist_ok=True)
    os.makedirs("sample_data", exist_ok=True)

def get_font(size):
    # Try loading crisp system fonts, fallback to default
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_label(filename, title, details, warning_text, warning_header="GOVERNMENT WARNING:", bg_color=(250, 248, 242)):
    img = Image.new("RGB", (1000, 1400), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(36)
    font_body = get_font(26)
    font_warn_hdr = get_font(24)
    font_warn_body = get_font(20)

    # Outer decorative border
    draw.rectangle([25, 25, 975, 1375], outline=(40, 30, 20), width=8)
    draw.rectangle([45, 45, 955, 1355], outline=(180, 150, 90), width=3)
    
    # Title / Brand Name
    draw.text((500, 120), title, fill=(20, 20, 20), font=font_title, anchor="mm")
    
    # Details lines
    y = 260
    for key, val in details.items():
        text = f"{key}: {val}"
        draw.text((500, y), text, fill=(30, 30, 30), font=font_body, anchor="mm")
        y += 60
        
    # Divider line
    draw.line([(100, y + 20), (900, y + 20)], fill=(180, 150, 90), width=4)
    
    # Government Warning Box
    y_warn = y + 70
    draw.rectangle([80, y_warn, 920, 1300], outline=(40, 40, 40), width=3)
    
    if warning_header:
        draw.text((110, y_warn + 35), warning_header, fill=(0, 0, 0), font=font_warn_hdr, anchor="lm")
    
    lines = warning_text.split("\n")
    line_y = y_warn + 85
    for line in lines:
        draw.text((110, line_y), line, fill=(20, 20, 20), font=font_warn_body, anchor="lm")
        line_y += 40

    filepath = os.path.join("sample_data/labels", filename)
    img.save(filepath, quality=95)
    return filepath

def generate_50_samples():
    create_directories()
    
    gov_warning_correct = (
        "(1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK\n"
        "ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF\n"
        "BIRTH DEFECTS.\n"
        "(2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY\n"
        "TO DRIVE A CAR OR OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS."
    )
    gov_warning_flat = gov_warning_correct.replace('\n', ' ')

    samples = []
    
    beverages = [
        ("BOURBON", "KENTUCKY STRAIGHT BOURBON WHISKEY", "45.0%", "90", "750 ML", "HIGHLAND DISTILLING CO., LOUISVILLE, KY", "PRODUCT OF USA"),
        ("SCOTCH", "SINGLE MALT SCOTCH WHISKY", "43.0%", "86", "750 ML", "GLEN LIVET DISTILLERY, SPEYSIDE", "PRODUCT OF SCOTLAND"),
        ("RYE_WHISKEY", "STRAIGHT RYE WHISKEY", "50.0%", "100", "750 ML", "OLD OVERHOLT DISTILLING, PA", "PRODUCT OF USA"),
        ("RED_WINE", "CABERNET SAUVIGNON RED WINE", "14.5%", "N/A", "750 ML", "NAPA VALLEY CELLARS, NAPA, CA", "PRODUCT OF USA"),
        ("WHITE_WINE", "CHARDONNAY WHITE WINE", "13.5%", "N/A", "750 ML", "SONOMA COAST VINEYARDS, CA", "PRODUCT OF USA"),
        ("ROSE_WINE", "PROVENCE ROSE WINE", "12.5%", "N/A", "750 ML", "DOMAINE DE LA ROSE, PROVENCE", "PRODUCT OF FRANCE"),
        ("CHAMPAGNE", "BRUT CHAMPAGNE", "12.0%", "N/A", "750 ML", "MAISON DE CHAMPAGNE, REIMS", "PRODUCT OF FRANCE"),
        ("TEQUILA_BLANCO", "TEQUILA BLANCO 100% AGAVE", "40.0%", "80", "750 ML", "AGAVE REAL S.A. DE C.V., JALISCO", "PRODUCT OF MEXICO"),
        ("TEQUILA_ANEJO", "TEQUILA ANEJO 100% AGAVE", "40.0%", "80", "750 ML", "DON JULIO S.A., JALISCO", "PRODUCT OF MEXICO"),
        ("DARK_RUM", "AGED DARK RUM", "40.0%", "80", "750 ML", "CARIBBEAN DISTILLERS, BARBADOS", "PRODUCT OF BARBADOS"),
        ("WHITE_RUM", "SUPERIOR WHITE RUM", "37.5%", "75", "750 ML", "BACARDI BOTTLING, PUERTO RICO", "PRODUCT OF PUERTO RICO"),
        ("VODKA", "PREMIUM GRAIN VODKA", "40.0%", "80", "750 ML", "POLAR SPIRITS, MINNEAPOLIS, MN", "PRODUCT OF USA"),
        ("LONDON_DRY_GIN", "LONDON DRY GIN", "47.3%", "94.6", "750 ML", "BEEFEATER DISTILLERY, LONDON", "PRODUCT OF UK"),
        ("CRAFT_IPA", "INDIA PALE ALE BEER", "6.8%", "N/A", "12 FL OZ", "SIERRA NEVADA BREWING, CA", "PRODUCT OF USA"),
        ("STOUT_BEER", "IMPERIAL OATMEAL STOUT BEER", "8.5%", "N/A", "16 FL OZ", "LEFT HAND BREWING, CO", "PRODUCT OF USA"),
        ("PILSNER_BEER", "GERMAN STYLE PILSNER BEER", "5.0%", "N/A", "12 FL OZ", "BAVARIA BREWING, MUNCHEN", "PRODUCT OF GERMANY"),
        ("HARD_CIDER", "CRISP APPLE HARD CIDER", "5.5%", "N/A", "12 FL OZ", "ANGRY ORCHARD CIDER, NY", "PRODUCT OF USA"),
        ("BRANDY", "CALIFORNIA AGED BRANDY", "40.0%", "80", "750 ML", "E&J DISTILLERS, MODESTO, CA", "PRODUCT OF USA"),
        ("MEZCAL", "MEZCAL ARTESANAL JOVEN", "45.0%", "90", "750 ML", "OAXACA ARTESANAL S.A., OAXACA", "PRODUCT OF MEXICO"),
        ("LIQUEUR", "TRIPLE SEC ORANGE LIQUEUR", "30.0%", "60", "750 ML", "COINTREAU S.A.R.L., ANGERS", "PRODUCT OF FRANCE")
    ]

    # CATEGORY 1: Pass Cases (Items 01 - 20)
    for idx, b in enumerate(beverages, start=1):
        filename = f"pass_{idx:02d}_{b[0].lower()}.png"
        brand_name = f"ESTATE RESERVE {b[0]}"
        draw_label(
            filename,
            brand_name,
            {
                "CLASS": b[1],
                "ALCOHOL CONTENT": f"{b[2]} ABV",
                "PROOF": f"{b[3]} PROOF" if b[3] != "N/A" else "N/A",
                "NET CONTENTS": b[4],
                "BOTTLER": b[5],
                "COUNTRY OF ORIGIN": b[6]
            },
            gov_warning_correct
        )
        samples.append({
            "scenario_id": f"pass-{idx:02d}",
            "scenario_title": f"Pass Case {idx:02d}: {b[0]}",
            "application_id": f"COLA-PASS-2026-{idx:02d}",
            "brand_name": brand_name,
            "class_type": b[1],
            "alcohol_content": b[2],
            "proof": b[3],
            "net_contents": b[4],
            "bottler_producer": b[5],
            "country_of_origin": b[6],
            "government_warning": f"GOVERNMENT WARNING: {gov_warning_flat}",
            "image_filename": filename,
            "expected_outcome": "PASS",
            "demo_description": f"Perfect match on all metadata fields & compliant CFR 16 warning for {b[0]}."
        })

    # CATEGORY 2: Field Mismatch Fail Cases (Items 21 - 30)
    mismatches = [
        ("fail_mismatch_21_abv.png", "ABV Mismatch (14.8% metadata vs 13.5% label)", "RED WINE", "14.8%", "13.5%"),
        ("fail_mismatch_22_net_contents.png", "Net Contents Mismatch (750 ML metadata vs 1 L label)", "BOURBON", "750 ML", "1 L"),
        ("fail_mismatch_23_brand_name.png", "Brand Name Mismatch (OLD CROWN vs CROWN RESERVE)", "WHISKEY", "OLD CROWN", "CROWN RESERVE"),
        ("fail_mismatch_24_class_type.png", "Class Designation Mismatch (BOURBON vs RYE)", "SPIRITS", "KENTUCKY STRAIGHT BOURBON", "STRAIGHT RYE WHISKEY"),
        ("fail_mismatch_25_missing_origin.png", "Missing Country of Origin on Imported Tequila", "TEQUILA", "PRODUCT OF MEXICO", ""),
        ("fail_mismatch_26_proof.png", "Proof Mismatch (100 Proof vs 80 Proof)", "RUM", "100", "80"),
        ("fail_mismatch_27_bottler.png", "Bottler Address Mismatch", "VODKA", "DISTILLERS LLC, NY", "DISTILLERS LLC, CA"),
        ("fail_mismatch_28_beer_abv.png", "Beer ABV Mismatch (8.5% vs 5.0%)", "BEER", "8.5%", "5.0%"),
        ("fail_mismatch_29_gin_net.png", "Gin Net Contents Mismatch (1 L vs 750 ML)", "GIN", "1 L", "750 ML"),
        ("fail_mismatch_30_cider_origin.png", "Missing Origin on Cider Import", "CIDER", "PRODUCT OF UK", "")
    ]

    for idx, m in enumerate(mismatches, start=21):
        filename = m[0]
        draw_label(
            filename,
            "MISMATCH TEST BRAND",
            {
                "CLASS": m[2],
                "ALCOHOL CONTENT": "13.5% ABV",
                "NET CONTENTS": "750 ML",
                "BOTTLER": "TEST DISTILLING CO., NY"
            },
            gov_warning_correct
        )
        samples.append({
            "scenario_id": f"fail-{idx:02d}",
            "scenario_title": f"Fail Case {idx:02d}: {m[1]}",
            "application_id": f"COLA-FAIL-2026-{idx:02d}",
            "brand_name": "MISMATCH TEST BRAND",
            "class_type": m[2],
            "alcohol_content": m[3],
            "proof": "N/A",
            "net_contents": "750 ML",
            "bottler_producer": "TEST DISTILLING CO., NY",
            "country_of_origin": "PRODUCT OF USA",
            "government_warning": f"GOVERNMENT WARNING: {gov_warning_flat}",
            "image_filename": filename,
            "expected_outcome": "REJECT",
            "demo_description": m[1]
        })

    # CATEGORY 3: Capitalization & Accent Small Differences (Items 31 - 40)
    caps_cases = [
        ("caps_diff_31_tequila_accent.png", "Accent Character (EL TEQUILEÑO vs El Tequileno)", "EL TEQUILEÑO REPOSADO", "El Tequileno Reposado"),
        ("caps_diff_32_stones_throw_punctuation.png", "Punctuation (STONE'S THROW vs STONES THROW)", "STONE'S THROW BOURBON", "STONES THROW BOURBON"),
        ("caps_diff_33_mixed_case_brand.png", "Mixed Case Brand Name (Highland Reserve)", "HIGHLAND RESERVE", "Highland Reserve"),
        ("caps_diff_34_accent_french_wine.png", "French Accent Mark (CHÂTEAU BELLEVIEW)", "CHÂTEAU BELLEVIEW", "Chateau Belleview"),
        ("caps_diff_35_spacing_brand.png", "Multi-Space Difference (OAK & HOPS IPA)", "OAK  &  HOPS IPA", "OAK & HOPS IPA"),
        ("caps_diff_36_lowercase_class.png", "Lowercase Class (bourbon whiskey)", "KENTUCKY STRAIGHT BOURBON WHISKEY", "bourbon whiskey"),
        ("caps_diff_37_short_abbrev.png", "Abbreviation (ALC/VOL vs ALC. VOL.)", "45% ALC/VOL", "45% ALC. VOL."),
        ("caps_diff_38_title_case_bottler.png", "Title Case Bottler (Highland Distilling Co)", "HIGHLAND DISTILLING CO", "Highland Distilling Co"),
        ("caps_diff_39_german_umlaut.png", "German Umlaut (MÜNCHEN PILSNER)", "MÜNCHEN PILSNER", "Munchen Pilsner"),
        ("caps_diff_40_trailing_dot.png", "Trailing Punctuation (USA. vs USA)", "PRODUCT OF USA.", "PRODUCT OF USA")
    ]

    for idx, c in enumerate(caps_cases, start=31):
        filename = c[0]
        draw_label(
            filename,
            c[3],
            {
                "CLASS": "PREMIUM BEVERAGE",
                "ALCOHOL CONTENT": "40.0% ABV",
                "NET CONTENTS": "750 ML",
                "BOTTLER": "TEST BOTTLING CO., CA",
                "COUNTRY OF ORIGIN": "PRODUCT OF USA"
            },
            gov_warning_correct
        )
        samples.append({
            "scenario_id": f"caps-{idx:02d}",
            "scenario_title": f"Review Case {idx:02d}: {c[1]}",
            "application_id": f"COLA-CAPS-2026-{idx:02d}",
            "brand_name": c[2],
            "class_type": "PREMIUM BEVERAGE",
            "alcohol_content": "40.0%",
            "proof": "80",
            "net_contents": "750 ML",
            "bottler_producer": "TEST BOTTLING CO., CA",
            "country_of_origin": "PRODUCT OF USA",
            "government_warning": f"GOVERNMENT WARNING: {gov_warning_flat}",
            "image_filename": filename,
            "expected_outcome": "NEEDS REVIEW",
            "demo_description": c[1]
        })

    # CATEGORY 4: Government Warning Regulatory Failures (Items 41 - 50)
    warning_fails = [
        ("warning_fail_41_lowercase_header.png", "Header 'Government Warning:' in Title Case instead of ALL CAPS", "Government Warning:"),
        ("warning_fail_42_missing_surgeon_general.png", "Missing 'SURGEON GENERAL' pregnancy health risk statement", "GOVERNMENT WARNING: (1) WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES..."),
        ("warning_fail_43_missing_impairment.png", "Missing driving/machinery impairment statement", "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL..."),
        ("warning_fail_44_completely_missing.png", "Government Warning box completely missing from artwork", ""),
        ("warning_fail_45_typo_surgeon.png", "Spelling error in Surgeon General ('SURGEON GENRAL')", "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENRAL..."),
        ("warning_fail_46_small_header.png", "Lowercase header 'government warning:'", "government warning:"),
        ("warning_fail_47_missing_header_colon.png", "Missing colon after header 'GOVERNMENT WARNING'", "GOVERNMENT WARNING (1)..."),
        ("warning_fail_48_altered_wording.png", "Altered wording in health risks", "GOVERNMENT WARNING: (1) DRINKING MAY CAUSE PROBLEMS..."),
        ("warning_fail_49_missing_driving_clause.png", "Missing driving clause", "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL..."),
        ("warning_fail_50_no_warning_box.png", "Recycling text substituted for Government Warning", "ENJOY RESPONSIBLY. PLEASE RECYCLE.")
    ]

    for idx, w in enumerate(warning_fails, start=41):
        filename = w[0]
        draw_label(
            filename,
            "WARNING TEST BRAND",
            {
                "CLASS": "BEER",
                "ALCOHOL CONTENT": "5.0% ABV",
                "NET CONTENTS": "12 FL OZ",
                "BOTTLER": "WARNING BREWING CO, CA",
                "COUNTRY OF ORIGIN": "PRODUCT OF USA"
            },
            w[2] if w[2] else "RECYCLE THIS BOTTLE.",
            warning_header="" if not w[2] else w[2].split(" ")[0] + " " + w[2].split(" ")[1] if len(w[2].split(" ")) > 1 else w[2]
        )
        samples.append({
            "scenario_id": f"warning-{idx:02d}",
            "scenario_title": f"Warning Fail {idx:02d}: {w[1]}",
            "application_id": f"COLA-WARN-2026-{idx:02d}",
            "brand_name": "WARNING TEST BRAND",
            "class_type": "BEER",
            "alcohol_content": "5.0%",
            "proof": "N/A",
            "net_contents": "12 FL OZ",
            "bottler_producer": "WARNING BREWING CO, CA",
            "country_of_origin": "PRODUCT OF USA",
            "government_warning": f"GOVERNMENT WARNING: {gov_warning_flat}",
            "image_filename": filename,
            "expected_outcome": "REJECT",
            "demo_description": w[1]
        })

    fieldnames = [
        "scenario_id", "scenario_title", "application_id", "brand_name", 
        "class_type", "alcohol_content", "proof", "net_contents", 
        "bottler_producer", "country_of_origin", "government_warning", 
        "image_filename", "expected_outcome", "demo_description"
    ]
    with open("sample_data/applications_metadata.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(samples)

    print("Generated 50 high-resolution test label artwork images in sample_data/labels/ and sample_data/applications_metadata.csv")

if __name__ == "__main__":
    generate_50_samples()
