import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
    const sizeClasses = {
        sm: 'w-5 h-5',
        md: 'w-8 h-8',
        lg: 'w-12 h-12',
    };

    return (
        <div className="flex flex-col items-center justify-center py-12 gap-4">
            <Loader2 className={`${sizeClasses[size]} text-primary-500 animate-spin`} />
            {text && <p className="text-gray-400">{text}</p>}
        </div>
    );
}
