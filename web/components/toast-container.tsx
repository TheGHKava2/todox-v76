import React from "react";
import { useToast, Toast } from "./toast-context";

const toastStyles = {
  success: "bg-green-100 border-green-500 text-green-800",
  error: "bg-red-100 border-red-500 text-red-800",
  warning: "bg-yellow-100 border-yellow-500 text-yellow-800",
  info: "bg-blue-100 border-blue-500 text-blue-800",
};

const toastIcons = {
  success: "✅",
  error: "❌",
  warning: "⚠️",
  info: "ℹ️",
};

interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

function ToastItem({ toast, onRemove }: ToastItemProps) {
  return (
    <div
      className={`
        fixed top-4 right-4 z-50 max-w-sm w-full
        border-l-4 p-4 rounded-md shadow-lg
        transform transition-all duration-300 ease-in-out
        hover:scale-105 cursor-pointer
        ${toastStyles[toast.type]}
      `}
      onClick={() => onRemove(toast.id)}
      style={{
        animation: "slideInRight 0.3s ease-out",
      }}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0 mr-3">
          <span className="text-lg">{toastIcons[toast.type]}</span>
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-sm mb-1">{toast.title}</h4>
          {toast.description && (
            <p className="text-xs opacity-90">{toast.description}</p>
          )}
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove(toast.id);
          }}
          className="ml-2 text-lg leading-none opacity-60 hover:opacity-100"
        >
          ×
        </button>
      </div>
    </div>
  );
}

export function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <>
      <style jsx global>{`
        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
      <div className="fixed top-0 right-0 z-50 p-4 pointer-events-none">
        <div className="space-y-2 pointer-events-auto">
          {toasts.map((toast, index) => (
            <div
              key={toast.id}
              style={{
                transform: `translateY(${index * 10}px)`,
                zIndex: 50 - index,
              }}
            >
              <ToastItem toast={toast} onRemove={removeToast} />
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
