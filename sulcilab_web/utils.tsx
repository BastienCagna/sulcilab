

function formatDate(dateString: string) {
    const d = new Date(Date.parse(dateString));
    return d.toLocaleString('en', {dateStyle: "short", timeStyle:"short"})
}

export {formatDate};