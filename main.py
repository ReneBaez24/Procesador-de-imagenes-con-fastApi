from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import io
import os
import uuid
from pathlib import Path

app = FastAPI(
    title="API de Procesamiento de Imagenes",
    description="API para agregar texto a imagenes en coordenadas especificas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringir esto al dominio especifico que usen 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def agregar_texto_a_imagen(
    imagen_bytes: bytes,
    texto: str,
    x: int,
    y: int,
    tamaño_fuente: int = 40,
    color_texto: str = "black"
) -> bytes:
    """
    Agrega texto a una imagen en las coordenadas especificadas
    
    Args:
        imagen_bytes: Bytes de la imagen original
        texto: Texto a agregar
        x: Coordenada X
        y: Coordenada Y
        tamaño_fuente: Tamaño de la fuente
        color_texto: Color del texto en formato RGB o nombre
    
    Returns:
        Bytes de la imagen procesada
    """
    try:
        # Abrir imagen desde bytes
        imagen = Image.open(io.BytesIO(imagen_bytes))
        
        # Convertir a RGB si es necesario
        if imagen.mode in ('RGBA', 'LA', 'P'):
            fondo = Image.new('RGB', imagen.size, (255, 255, 255))
            if imagen.mode == 'P':
                imagen = imagen.convert('RGBA')
            fondo.paste(imagen, mask=imagen.split()[-1] if imagen.mode == 'RGBA' else None)
            imagen = fondo
        
        # Preparar para dibujar
        draw = ImageDraw.Draw(imagen)
        
        # Intentar cargar fuentes en diferentes ubicaciones
        fuentes_posibles = [
            "arial.ttf",
            "arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf"
        ]
        
        fuente = None
        for fuente_path in fuentes_posibles:
            try:
                fuente = ImageFont.truetype(fuente_path, tamaño_fuente)
                break
            except:
                continue
        
        # Si no se encuentra ninguna fuente, usar la por defecto
        if fuente is None:
            fuente = ImageFont.load_default()
        
        # Agregar texto
        draw.text((x, y), texto, fill=color_texto, font=fuente)
        
        # Guardar en buffer
        buffer = io.BytesIO()
        imagen.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        
        return buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

@app.post("/api/procesar-imagen")
async def procesar_imagen(
    imagen: UploadFile = File(..., description="Archivo de imagen a procesar"),
    texto: str = Form(..., description="Texto a agregar a la imagen"),
    x: int = Form(..., description="Coordenada X donde agregar el texto"),
    y: int = Form(..., description="Coordenada Y donde agregar el texto"),
    tamaño_fuente: Optional[int] = Form(40, description="Tamaño de la fuente"),
    color_texto: Optional[str] = Form("black", description="Color del texto")
):
    """
    Procesa una imagen agregando texto y la devuelve sin guardarla en disco.
    """

    # Validar tipo de archivo
    if not imagen.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    try:
        # Leer imagen en bytes
        contenido = await imagen.read()

        # Procesar imagen
        imagen_procesada_bytes = agregar_texto_a_imagen(
            contenido, texto, x, y, tamaño_fuente, color_texto
        )

        # Devolver la imagen sin guardarla en disco
        return StreamingResponse(
            io.BytesIO(imagen_procesada_bytes),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f'attachment; filename="imagen_procesada_{texto[:20]}.jpg"'
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.post("/api/procesar-imagen-base64")
async def procesar_imagen_base64(
    texto: str = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    imagen_base64: str = Form(..., description="Imagen en base64"),
    tamaño_fuente: Optional[int] = Form(40),
    color_texto: Optional[str] = Form("black")
):
    """
    Version alternativa que recibe la imagen en base64
    util para aplicaciones web que prefieran enviar base64
    """
    try:
        import base64
        
        # Decodificar base64
        if "," in imagen_base64:
            # Si viene con prefijo data:image/...
            imagen_base64 = imagen_base64.split(",")[1]
        
        imagen_bytes = base64.b64decode(imagen_base64)
        
        # Procesar imagen
        imagen_procesada_bytes = agregar_texto_a_imagen(
            imagen_bytes, texto, x, y, tamaño_fuente, color_texto
        )
        
        # Convertir a base64 para respuesta
        imagen_base64_procesada = base64.b64encode(imagen_procesada_bytes).decode('utf-8')
        
        return JSONResponse({
            "success": True,
            "imagen_procesada": f"data:image/jpeg;base64,{imagen_base64_procesada}",
            "filename": f"imagen_procesada_{texto[:20]}.jpg"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

@app.post("/api/info-imagen")
async def info_imagen(
    imagen: UploadFile = File(..., description="Archivo de imagen")
):
    """
    Obtiene informacion basica de una imagen
    util para determinar coordenadas
    """
    try:
        contenido = await imagen.read()
        img = Image.open(io.BytesIO(contenido))
        
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_kb": len(contenido) / 1024
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo imagen: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    return {
        "status": "online",
        "service": "image-processor-api",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Pagina principal con documentacion"""
    return {
        "message": "API de Procesamiento de Imagenes",
        "endpoints": {
            "POST /api/procesar-imagen": "Procesa imagen con texto",
            "POST /api/procesar-imagen-base64": "Procesa imagen en base64",
            "GET /api/info-imagen": "Obtiene informacion de imagen",
            "GET /health": "Verifica estado del servidor",
            "GET /docs": "Documentacion interactiva (Swagger)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )