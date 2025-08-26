# Generación de Iconos para PWA

Para completar la configuración de la PWA, necesitas generar los iconos en los siguientes tamaños:

## Iconos Requeridos:
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

## Iconos de Atajos:
- shortcut-dashboard.png (96x96)
- shortcut-avance.png (96x96)
- shortcut-medicion.png (96x96)

## Screenshots:
- desktop-dashboard.png (1280x720)
- mobile-dashboard.png (375x667)

## Herramientas Recomendadas:

### Online:
- [PWA Builder](https://www.pwabuilder.com/imageGenerator)
- [Favicon Generator](https://realfavicongenerator.net/)

### Comando (si tienes ImageMagick):
```bash
# Desde un icono base de 512x512
convert icon-512x512.png -resize 72x72 icon-72x72.png
convert icon-512x512.png -resize 96x96 icon-96x96.png
convert icon-512x512.png -resize 128x128 icon-128x128.png
convert icon-512x512.png -resize 144x144 icon-144x144.png
convert icon-512x512.png -resize 152x152 icon-152x152.png
convert icon-512x512.png -resize 192x192 icon-192x192.png
convert icon-512x512.png -resize 384x384 icon-384x384.png
```

## Diseño Sugerido:
- Fondo: Azul (#3b82f6) o blanco
- Icono: Símbolo de telecomunicaciones, torre, o las letras "BDPA"
- Estilo: Moderno, limpio, legible en tamaños pequeños