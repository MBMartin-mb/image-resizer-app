# Image Resizer App

Jednoduchá webová aplikace pro úpravu obrázků. Umožňuje nahrát obrázek (JPEG/PNG) a automaticky vygenerovat tři varianty:
- Sociální sítě (1:1, 1080x1080px)
- Carousel na web (16:9, 1920x1080px)
- Statický banner (300x250px)

## Funkce
- Nahrávání obrázku přes webové rozhraní
- Automatický ořez s detekcí hlavního obsahu (pomocí OpenCV)
- Zobrazení náhledů a možnost stažení ve formátu PNG
- JSON s odkazy na vygenerované obrázky

## Technologie
- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: FastAPI, OpenCV, Python
- **Build**: Vite pro frontend, Uvicorn pro backend

## Požadavky
- Node.js (v18 nebo vyšší)
- Python (3.8 nebo vyšší)
- Git

## Instalace

### Krok 1: Klonování repozitáře
```bash
git clone https://github.com/vase-uzivatelske-jmeno/image-resizer-app.git
cd image-resizer-app
