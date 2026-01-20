import React, { useState } from 'react';
import { X, Upload, Image as ImageIcon } from 'lucide-react';
import { Button } from './button';

export const ImageUpload = ({ 
  onChange, 
  value = [], 
  maxFiles = 5, 
  maxSizeMB = 10,
  required = false,
  label = "Fotos hochladen"
}) => {
  // Initialize previews with existing value (Base64 strings)
  const [previews, setPreviews] = useState(value || []);
  const [error, setError] = useState('');
  
  // Update previews when value changes from parent
  React.useEffect(() => {
    if (value && value.length > 0 && previews.length === 0) {
      // If value contains Base64 strings, use them directly as previews
      setPreviews(value);
    }
  }, [value]);

  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    setError('');

    if (value.length + files.length > maxFiles) {
      setError(`Maximal ${maxFiles} Bilder erlaubt`);
      return;
    }

    const newBase64Files = [];

    for (const file of files) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError(`${file.name} ist kein Bild`);
        continue;
      }

      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setError(`${file.name}: Nur JPG, PNG, WEBP erlaubt`);
        continue;
      }

      // Validate file size
      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > maxSizeMB) {
        setError(`${file.name} ist zu groß (${sizeMB.toFixed(1)} MB). Max: ${maxSizeMB} MB`);
        continue;
      }

      // Convert to base64
      try {
        const base64 = await fileToBase64(file);
        newBase64Files.push(base64);
      } catch (err) {
        setError(`Fehler beim Laden von ${file.name}`);
      }
    }

    const updatedBase64 = [...value, ...newBase64Files];
    
    // Update both previews and value with Base64 strings
    setPreviews(updatedBase64);
    onChange(updatedBase64);
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  const removeImage = (index) => {
    const updatedBase64 = value.filter((_, i) => i !== index);
    
    // Revoke the blob URL to free memory (only if it's a blob URL, not Base64)
    if (previews[index] && previews[index].startsWith('blob:')) {
      URL.revokeObjectURL(previews[index]);
    }
    
    // Update both previews and value
    setPreviews(updatedBase64);
    onChange(updatedBase64);
    setError('');
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <span className="text-xs text-gray-500">
          {value.length}/{maxFiles} Bilder
        </span>
      </div>

      {/* Preview Grid */}
      {previews.length > 0 && (
        <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
          {previews.map((preview, index) => (
            <div key={index} className="relative group">
              <img
                src={preview}
                alt={`Preview ${index + 1}`}
                className="w-full h-24 object-cover rounded-lg border-2 border-gray-200"
              />
              <button
                type="button"
                onClick={() => removeImage(index)}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload Button */}
      {value.length < maxFiles && (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
          <input
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/webp"
            multiple
            onChange={handleFileChange}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <div className="flex flex-col items-center gap-2">
              <div className="p-3 bg-gray-100 rounded-full">
                <Upload className="w-6 h-6 text-gray-600" />
              </div>
              <div className="text-sm text-gray-600">
                <span className="font-medium text-yellow-600">Klicken Sie zum Hochladen</span>
                <p className="text-xs text-gray-500 mt-1">
                  JPG, PNG, WEBP (max. {maxSizeMB} MB pro Bild)
                </p>
              </div>
            </div>
          </label>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 text-red-600 text-sm p-3 bg-red-50 rounded-lg">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* Info Text */}
      {required && value.length === 0 && (
        <p className="text-xs text-gray-500">
          Mindestens 1 Foto erforderlich für Bewertungen mit 1-3 Sternen
        </p>
      )}
    </div>
  );
};
