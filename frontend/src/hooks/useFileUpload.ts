import { useState, useRef, RefObject } from 'react';
import { validateFiles } from '../utils/fileValidation';

interface UseFileUploadReturn {
  files: File[];
  fileInputRef: RefObject<HTMLInputElement | null>;
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  removeFile: (indexToRemove: number) => void;
  handleUploadClick: () => void;
  clearFiles: () => void;
}

export const useFileUpload = (isUploading: boolean): UseFileUploadReturn => {
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      const validFiles = validateFiles(newFiles);

      setFiles(prev => {
        const existingNames = new Set(prev.map(f => f.name));
        const uniqueNewFiles = validFiles.filter(f => !existingNames.has(f.name));
        return [...prev, ...uniqueNewFiles];
      });
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeFile = (indexToRemove: number) => {
    setFiles(prev => prev.filter((_, i) => i !== indexToRemove));
  };

  const handleUploadClick = () => {
    if (!isUploading) fileInputRef.current?.click();
  };

  const clearFiles = () => {
    setFiles([]);
  };

  return { files, fileInputRef, handleFileChange, removeFile, handleUploadClick, clearFiles };
};
