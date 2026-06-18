export const isValidFileType = (file: File): boolean => {
  return ["image/jpeg", "image/png", "image/jpg", "application/pdf"].includes(
    file.type,
  );
};

export const isValidFileSize = (file: File): boolean => {
  return file.size <= 5 * 1024 * 1024;
};

export const validateFiles = (files: File[]): File[] => {
  return files.filter((f) => {
    const isValidType = isValidFileType(f);
    const isValidSize = isValidFileSize(f);
    if (!isValidType) alert(`Invalid file type: ${f.name}`);
    if (!isValidSize) alert(`File too large (max 5MB): ${f.name}`);
    return isValidType && isValidSize;
  });
};
