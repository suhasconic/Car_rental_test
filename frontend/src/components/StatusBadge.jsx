import { Clock, CheckCircle, XCircle, AlertTriangle, Trophy, Loader } from 'lucide-react';

const statusConfig = {
    pending: {
        icon: Clock,
        class: 'status-pending',
        label: 'Pending',
    },
    competing: {
        icon: Trophy,
        class: 'status-competing',
        label: 'In Auction',
    },
    confirmed: {
        icon: CheckCircle,
        class: 'status-confirmed',
        label: 'Confirmed',
    },
    rejected: {
        icon: XCircle,
        class: 'status-rejected',
        label: 'Rejected',
    },
    cancelled: {
        icon: XCircle,
        class: 'status-cancelled',
        label: 'Cancelled',
    },
    completed: {
        icon: CheckCircle,
        class: 'status-confirmed',
        label: 'Completed',
    },
    active: {
        icon: Loader,
        class: 'status-active',
        label: 'Active',
    },
    closed: {
        icon: CheckCircle,
        class: 'status-closed',
        label: 'Closed',
    },
    damaged: {
        icon: AlertTriangle,
        class: 'status-rejected',
        label: 'Damaged',
    },
};

export default function StatusBadge({ status }) {
    const config = statusConfig[status?.toLowerCase()] || statusConfig.pending;
    const Icon = config.icon;

    return (
        <span className={`status-badge ${config.class}`}>
            <Icon className="w-3 h-3" />
            {config.label}
        </span>
    );
}
