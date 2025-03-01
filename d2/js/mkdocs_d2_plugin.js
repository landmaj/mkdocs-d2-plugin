function d2OpenInNewTab(svgID) {
    const container = document.getElementById(svgID);
    const svg = container ? container.querySelector('svg') : null;
    if (!svg) return;

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = svg.outerHTML;

    const links = tempDiv.querySelectorAll('a');
    links.forEach(link => {
        link.setAttribute('onmouseover', 'this.style.textDecoration="underline"');
        link.setAttribute('onmouseout', 'this.style.textDecoration="none"');
        link.setAttribute('target', '_blank');
    });

    const blob = new Blob([tempDiv.innerHTML], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const win = window.open(url);

    if (win) {
        win.onload = () => URL.revokeObjectURL(url);
    }
}
