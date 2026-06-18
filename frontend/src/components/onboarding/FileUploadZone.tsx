import React from "react";

interface FileUploadZoneProps {
  files: File[];
  isUploading: boolean;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  removeFile: (indexToRemove: number) => void;
  handleUploadClick: () => void;
}

export function FileUploadZone({
  files,
  isUploading,
  fileInputRef,
  handleFileChange,
  removeFile,
  handleUploadClick,
}: FileUploadZoneProps) {
  return (
    <>
      <input
        type="file"
        multiple
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="application/pdf,image/png,image/jpeg,image/jpg"
      />

      <div
        role="button"
        tabIndex={isUploading ? -1 : 0}
        onClick={handleUploadClick}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleUploadClick();
          }
        }}
        aria-label="Upload utility bills"
        aria-live="polite"
        aria-busy={isUploading}
        className={`w-full border-2 border-dashed rounded-2xl p-10 text-center mb-8 transition-transform focus:outline-none focus:ring-4 focus:ring-emerald-500/50 ${
          isUploading
            ? "border-emerald-500 bg-emerald-50 cursor-wait relative overflow-hidden"
            : files.length > 0
              ? "border-emerald-500 bg-emerald-50 hover:bg-emerald-100 cursor-pointer"
              : "border-slate-300 hover:border-emerald-400 hover:bg-slate-50 cursor-pointer"
        }`}
      >
        {isUploading ? (
          <div className="flex flex-col items-center w-full">
            <div className="absolute top-0 left-0 right-0 h-1 bg-emerald-400 opacity-80 animate-[scan_2s_linear_infinite]"></div>
            <svg
              className="w-12 h-12 text-emerald-500 mb-4 animate-pulse"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span className="text-emerald-800 font-bold mb-2 animate-pulse">
              Running Local OCR Model...
            </span>
            <p className="text-sm text-emerald-600/70">
              Extracting text, values, and vendor details
            </p>
          </div>
        ) : files.length > 0 ? (
          <div className="flex flex-col items-center w-full">
            <svg
              className="w-12 h-12 text-emerald-500 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="text-emerald-800 font-bold mb-4">
              {files.length} file{files.length > 1 ? "s" : ""} selected
            </span>
            <div className="flex flex-wrap gap-2 justify-center w-full max-h-[120px] overflow-y-auto pb-2">
              {files.map((f, idx) => (
                <div
                  key={`${f.name}-${f.lastModified}`}
                  className="bg-white border border-emerald-200 text-emerald-700 text-xs px-3 py-1.5 rounded-full flex items-center gap-2 shadow-sm"
                >
                  <span className="max-w-[120px] truncate">{f.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(idx);
                    }}
                    className="hover:bg-emerald-100 rounded-full p-0.5 text-emerald-500 hover:text-emerald-800 transition-colors"
                  >
                    <svg
                      className="w-3.5 h-3.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="w-14 h-14 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-slate-400 group-hover:text-emerald-500 transition-colors">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                />
              </svg>
            </div>
            <span className="text-slate-700 font-semibold">
              Click to upload multiple bills (PDF/PNG)
            </span>
            <p className="text-sm text-slate-500 mt-2">
              Personal data is scrubbed locally.
            </p>
          </div>
        )}
      </div>
    </>
  );
}
