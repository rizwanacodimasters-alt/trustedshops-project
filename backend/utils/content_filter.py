"""
Content filtering and moderation for reviews
"""

import re
from typing import List, Dict, Tuple

# Blacklisted keywords - Basic filters
GENERAL_BLACKLIST = [
    # Beleidigungen (Deutsch)
    r'\b(idiot|dummkopf|arschloch|scheisse|scheiße|fick|hurensohn|wichser)\b',
    # Beleidigungen (Englisch)
    r'\b(fuck|shit|asshole|bastard|bitch|damn)\b',
    # Rassismus
    r'\b(nazi|rassist|nigger|kanake)\b',
]

# Personal data patterns
PERSONAL_DATA_PATTERNS = [
    (r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', 'E-Mail-Adresse'),  # Email
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'Kreditkartennummer'),  # Credit card
    (r'\bIBAN\s*[A-Z]{2}\d{2}[\s\d]+\b', 'IBAN'),  # IBAN
    (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', 'Telefonnummer'),  # Phone
]

# Industry-specific filters
INDUSTRY_FILTERS = {
    'insurance': [
        (r'\bVersicherungsnummer\b', 'Versicherungsdaten'),
        (r'\bPolice\s*Nr\b', 'Versicherungsdaten'),
        (r'\bKontonummer\b', 'Bankdaten'),
    ],
    'ecig': [
        (r'\b(e-liquid|liquid|nikotin|dampf|vape)\b', 'Produkterwähnung'),
        (r'\b(rauchen|dampfen)\b', 'Konsumhinweis'),
    ],
    'medicine': [
        (r'\b(wirksam|wirkung|heilung|heilt|therapie)\b', 'Wirksamkeitsaussage'),
        (r'\b(vorher|nachher|before|after)\b', 'Vorher-Nachher-Vergleich'),
    ],
    'supplements': [
        (r'\b(wirksam|wirkung|abnehmen|muskelaufbau)\b', 'Wirksamkeitsaussage'),
        (r'\b(vorher|nachher|before|after)\b', 'Vorher-Nachher-Vergleich'),
    ],
    'alcohol': [
        (r'\b(alkohol|bier|wein|schnaps|wodka|whisky)\b', 'Alkoholwerbung'),
        (r'\b(betrunken|besaufen|saufen)\b', 'Alkoholkonsum'),
    ],
}


def check_content(text: str, industry: str = None) -> Tuple[bool, List[str], List[str]]:
    """
    Check review content for violations.
    
    Args:
        text: Review text to check
        industry: Optional industry for specific filters
        
    Returns:
        Tuple of (is_clean, flags, reasons)
        - is_clean: True if no violations found
        - flags: List of violation types
        - reasons: List of human-readable reasons
    """
    if not text:
        return True, [], []
    
    text_lower = text.lower()
    flags = []
    reasons = []
    
    # Check general blacklist
    for pattern in GENERAL_BLACKLIST:
        if re.search(pattern, text_lower, re.IGNORECASE):
            flags.append('offensive_language')
            reasons.append('Enthält unangemessene Sprache')
            break
    
    # Check personal data
    for pattern, data_type in PERSONAL_DATA_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            flags.append('personal_data')
            reasons.append(f'Enthält {data_type}')
    
    # Check industry-specific filters
    if industry and industry in INDUSTRY_FILTERS:
        for pattern, violation_type in INDUSTRY_FILTERS[industry]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                flags.append(f'industry_{industry}')
                reasons.append(f'{violation_type} nicht erlaubt')
    
    is_clean = len(flags) == 0
    return is_clean, flags, reasons


def calculate_trust_score_grade(rating: float) -> Dict[str, str]:
    """
    Calculate Trusted Shops grade based on rating.
    
    Args:
        rating: Average rating (0.0 - 5.0)
        
    Returns:
        Dict with grade, label, and color
    """
    if rating >= 4.50:
        return {
            'grade': 'A',
            'label': 'Exzellent',
            'label_en': 'Excellent',
            'color': '#00B67A',
            'text_color': 'white'
        }
    elif rating >= 3.50:
        return {
            'grade': 'B',
            'label': 'Gut',
            'label_en': 'Good',
            'color': '#73CF11',
            'text_color': 'white'
        }
    elif rating >= 2.50:
        return {
            'grade': 'C',
            'label': 'Befriedigend',
            'label_en': 'Satisfactory',
            'color': '#FFCE00',
            'text_color': 'black'
        }
    elif rating >= 1.50:
        return {
            'grade': 'D',
            'label': 'Ausreichend',
            'label_en': 'Adequate',
            'color': '#FF8622',
            'text_color': 'white'
        }
    else:
        return {
            'grade': 'F',
            'label': 'Mangelhaft',
            'label_en': 'Poor',
            'color': '#FF3722',
            'text_color': 'white'
        }


def should_require_proof(rating: int) -> bool:
    """
    Determine if review requires proof upload.
    Low ratings (1-3 stars) require proof.
    
    Args:
        rating: Review rating (1-5)
        
    Returns:
        True if proof is required
    """
    return rating <= 3


def validate_image_file(base64_string: str, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate a single image file.
    
    Args:
        base64_string: Base64 encoded image string
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import base64
    import imghdr
    
    # Check if it starts with data URI
    if not base64_string.startswith('data:image/'):
        return False, "Datei muss ein Bild sein (JPG, PNG, WEBP)"
    
    # Extract mime type
    try:
        header, encoded = base64_string.split(',', 1)
        mime_type = header.split(':')[1].split(';')[0]
        
        # Check allowed image types
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if mime_type not in allowed_types:
            return False, f"Bildtyp {mime_type} nicht erlaubt. Nur JPG, PNG, WEBP erlaubt"
        
        # Decode and check size
        image_data = base64.b64decode(encoded)
        size_mb = len(image_data) / (1024 * 1024)
        
        if size_mb > max_size_mb:
            return False, f"Datei zu groß ({size_mb:.1f} MB). Maximum: {max_size_mb} MB"
        
        # Verify it's actually an image
        image_type = imghdr.what(None, h=image_data)
        if image_type not in ['jpeg', 'png', 'webp']:
            return False, "Datei ist kein gültiges Bild"
        
        return True, ""
        
    except Exception as e:
        return False, f"Ungültige Bilddatei: {str(e)}"


def validate_proof_data(proof_photos: List[str], proof_order: str, rating: int) -> Tuple[bool, str]:
    """
    Validate proof data for low-star reviews (1-3 stars).
    
    Args:
        proof_photos: List of base64 image strings
        proof_order: Order number
        rating: Review rating
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Only validate if rating requires proof
    if rating > 3:
        return True, ""
    
    # For 1-3 star reviews, photos and order number are required
    if not proof_photos or len(proof_photos) == 0:
        return False, "Mindestens 1 Produktfoto erforderlich für Bewertungen mit 1-3 Sternen"
    
    if len(proof_photos) > 5:
        return False, "Maximal 5 Fotos erlaubt"
    
    if not proof_order or len(proof_order) < 3:
        return False, "Gültige Bestellnummer erforderlich für Bewertungen mit 1-3 Sternen"
    
    # Validate each photo
    for i, photo in enumerate(proof_photos):
        is_valid, error = validate_image_file(photo, max_size_mb=10)
        if not is_valid:
            return False, f"Foto {i+1}: {error}"
    
    return True, ""
