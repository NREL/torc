/**
 * Torc Dashboard - Utility Methods
 * Helper functions and formatters
 */

Object.assign(TorcDashboard.prototype, {
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    },

    escapeHtml(str) {
        if (str === null || str === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    },

    truncateId(id) {
        if (!id) return '-';
        return id.length > 8 ? id.substring(0, 8) + '...' : id;
    },

    truncate(str, maxLen) {
        if (!str) return '';
        return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
    },

    formatDate(dateStr) {
        if (!dateStr) return '-';
        try {
            const date = new Date(dateStr);
            return date.toLocaleString();
        } catch {
            return dateStr;
        }
    },

    formatTimestamp(timestamp) {
        if (!timestamp) return '-';
        try {
            const date = new Date(timestamp);
            return this.formatDateLocal(date);
        } catch {
            return timestamp;
        }
    },

    formatUnixTimestamp(unixTime) {
        if (unixTime == null) return '-';
        try {
            // Unix timestamp is in seconds (as a float)
            const date = new Date(unixTime * 1000);
            return this.formatDateLocal(date);
        } catch {
            return '-';
        }
    },

    formatDateLocal(date) {
        // Format as YYYY-MM-DD HH:MM:SS in local timezone
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },

    formatBytes(bytes) {
        if (bytes == null) return '-';
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    highlightJson(jsonString) {
        // Escape HTML first
        let escaped = this.escapeHtml(jsonString);

        // Replace JSON syntax elements with colored spans
        // Order matters here - we do replacements in a specific order

        // Strings (both keys and values) - careful with the pattern
        escaped = escaped.replace(
            /(&quot;)([^&]*?)(&quot;)/g,
            (match, q1, content, q2) => {
                return `<span class="json-string">${q1}${content}${q2}</span>`;
            }
        );

        // Numbers
        escaped = escaped.replace(
            /(?<![a-zA-Z\-])(-?\d+\.?\d*)(?![a-zA-Z])/g,
            '<span class="json-number">$1</span>'
        );

        // Booleans
        escaped = escaped.replace(/\b(true|false)\b/g, '<span class="json-boolean">$1</span>');

        // Null
        escaped = escaped.replace(/\bnull\b/g, '<span class="json-null">null</span>');

        // Brackets and braces
        escaped = escaped.replace(/([{}\[\]])/g, '<span class="json-bracket">$1</span>');

        return escaped;
    },
});
