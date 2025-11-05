import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  fullscreen?: boolean;
}

const sizeClasses = {
  sm: "w-4 h-4",
  md: "w-6 h-6",
  lg: "w-8 h-8",
};

export function LoadingSpinner({
  size = "md",
  text,
  fullscreen = false,
}: LoadingSpinnerProps) {
  const spinner = (
    <div className="flex items-center justify-center space-x-2">
      <div
        className={`${sizeClasses[size]} border-2 border-blue-200 border-t-blue-600 rounded-full animate-spin`}
      ></div>
      {text && <span className="text-sm text-gray-600">{text}</span>}
    </div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg shadow-lg">{spinner}</div>
      </div>
    );
  }

  return spinner;
}

interface LoadingButtonProps {
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  type?: "button" | "submit";
}

export function LoadingButton({
  loading = false,
  disabled = false,
  children,
  onClick,
  className = "",
  type = "button",
}: LoadingButtonProps) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={loading || disabled}
      className={`
        relative inline-flex items-center px-4 py-2 border border-transparent 
        text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 
        hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 
        focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed
        transition-all duration-200
        ${className}
      `}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <LoadingSpinner size="sm" />
        </div>
      )}
      <span className={loading ? "opacity-0" : "opacity-100"}>{children}</span>
    </button>
  );
}

interface LoadingStateProps {
  loading: boolean;
  error?: string | null;
  empty?: boolean;
  emptyMessage?: string;
  children: React.ReactNode;
  loadingText?: string;
}

export function LoadingState({
  loading,
  error,
  empty,
  emptyMessage = "Nenhum item encontrado",
  children,
  loadingText = "Carregando...",
}: LoadingStateProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" text={loadingText} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-2">😵</div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            Ops! Algo deu errado
          </h3>
          <p className="text-sm text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  if (empty) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-gray-400 text-4xl mb-2">📭</div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            Nada por aqui
          </h3>
          <p className="text-sm text-gray-500">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
