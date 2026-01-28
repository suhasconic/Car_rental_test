import { Shield, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function TrustBadge({ score, size = 'md', showLabel = false }) {
    const numericScore = parseFloat(score) || 0;

    let colorClass, label, Icon;

    if (numericScore >= 80) {
        colorClass = 'trust-excellent';
        label = 'Excellent';
        Icon = TrendingUp;
    } else if (numericScore >= 50) {
        colorClass = 'trust-good';
        label = 'Good';
        Icon = TrendingUp;
    } else if (numericScore >= 30) {
        colorClass = 'trust-average';
        label = 'Average';
        Icon = Minus;
    } else {
        colorClass = 'trust-poor';
        label = 'Low';
        Icon = TrendingDown;
    }

    const sizeClasses = {
        sm: 'text-xs px-2 py-0.5',
        md: 'text-sm px-3 py-1',
        lg: 'text-base px-4 py-2',
    };

    return (
        <div className={`trust-badge ${colorClass} ${sizeClasses[size]}`}>
            <Shield className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />
            <span className="font-mono font-semibold">{numericScore.toFixed(1)}</span>
            {showLabel && <span className="font-sans ml-1">{label}</span>}
        </div>
    );
}
