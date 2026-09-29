import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { clsx } from 'clsx';
import { Toast as ToastType, ToastVariant } from '../../hooks/useToast';

interface ToastProps {
  toast: ToastType;
  onDismiss: (id: string) => void;
}

const variantConfig: Record<
  ToastVariant,
  { icon: React.ReactNode; className: string }
> = {
  success: {
    icon: <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />,
    className: 'border-green-200 bg-green-50',
  },
  error: {
    icon: <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />,
    className: 'border-red-200 bg-red-50',
  },
  info: {
    icon: <Info className="h-5 w-5 text-blue-500 shrink-0" />,
    className: 'border-blue-200 bg-blue-50',
  },
  warning: {
    icon: <AlertTriangle className="h-5 w-5 text-yellow-500 shrink-0" />,
    className: 'border-yellow-200 bg-yellow-50',
  },
};

export function Toast({ toast, onDismiss }: ToastProps) {
  const config = variantConfig[toast.variant];

  return (
    <div
      className={clsx(
        'flex items-start gap-3 rounded-xl border px-4 py-3 shadow-lg w-80 pointer-events-auto',
        config.className,
      )}
      role="alert"
    >
      {config.icon}
      <p className="flex-1 text-sm font-medium text-gray-800">{toast.message}</p>
      <button
        onClick={() => onDismiss(toast.id)}
        className="shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Dismiss"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

interface ToastContainerProps {
  toasts: ToastType[];
  onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  );
}
