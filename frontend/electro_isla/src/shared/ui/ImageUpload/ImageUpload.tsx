/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🖼️ COMPONENT - Image Upload with Drag & Drop
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState, useRef, useEffect } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { FiUpload, FiX, FiImage } from 'react-icons/fi';
import './ImageUpload.css';

interface ImageUploadProps {
  value: string | File | null;
  onChange: (file: File | string) => void;
  onFileSelect?: (file: File) => void;
}

export const ImageUpload = ({ value, onChange, onFileSelect }: ImageUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string>(typeof value === 'string' ? value : '');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ✅ Sincronizar preview cuando cambia el valor (para editar productos)
  useEffect(() => {
    if (typeof value === 'string') {
      setPreview(value);
    } else if (value === null) {
      setPreview('');
    }
  }, [value]);

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file: File) => {
    // Validar que sea imagen
    if (!file.type.startsWith('image/')) {
      alert('❌ Por favor selecciona una imagen válida\n\nFormatos soportados: PNG, JPG, GIF, WebP');
      return;
    }

    // Validar tamaño (máx 5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
      alert(`⚠️ Imagen demasiado grande\n\nLa imagen pesa ${sizeMB}MB\nMáximo permitido: 5MB\n\nPor favor comprime la imagen antes de subirla.`);
      return;
    }

    // ✅ NUEVO: Enviar archivo en lugar de Base64
    // Crear preview para mostrar en el formulario
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result as string;
      setPreview(result);
    };
    reader.readAsDataURL(file);
    
    // Enviar el archivo al formulario (será manejado por FormData)
    onChange(file);
    
    // Si hay callback para el archivo, llamarlo
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  const handleRemove = () => {
    setPreview('');
    onChange('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="image-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileInput}
        className="image-upload-input"
      />

      {preview ? (
        <div className="image-upload-preview">
          <img src={preview} alt="Preview" className="image-upload-preview-img" />
          <button
            type="button"
            className="image-upload-remove"
            onClick={handleRemove}
          >
            <FiX />
          </button>
        </div>
      ) : (
        <div
          className={`image-upload-dropzone ${isDragging ? 'dragging' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <FiImage className="image-upload-icon" />
          <p className="image-upload-text">
            Arrastra una imagen aquí o haz click para seleccionar
          </p>
          <p className="image-upload-hint">
            PNG, JPG, GIF hasta 5MB
          </p>
          <button type="button" className="image-upload-btn">
            <FiUpload />
            Seleccionar Imagen
          </button>
        </div>
      )}
    </div>
  );
};
