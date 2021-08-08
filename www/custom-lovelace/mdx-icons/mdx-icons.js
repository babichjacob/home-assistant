const icons = {
    "lenovo-smart-display": "M21.000,20.000 L3.000,20.000 C1.895,20.000 1.000,19.105 1.000,18.000 L1.000,6.000 C1.000,4.895 1.895,4.000 3.000,4.000 L21.000,4.000 C22.105,4.000 23.000,4.895 23.000,6.000 L23.000,18.000 C23.000,19.105 22.105,20.000 21.000,20.000 ZM21.000,6.000 L6.000,6.000 L6.000,18.000 L21.000,18.000 L21.000,6.000 Z",
    "google-home-mini": {
        path: "M156 1236c0-579.06 1044-524 1044-524s1044-55.06 1044 524c0 304.18-387 497-387 497H542l-.44-.73C515.91 1719.12 156 1529.34 156 1236zm1963 0c0-98.19 2.66-400-919-400s-919 301.81-919 400c0 62.18 28 121.47 66.69 173.71L307 1342h1786l-41.62 68.95c39.17-52.54 67.62-112.28 67.62-174.95z",
        viewBox: "0 0 2400 2400",
    },
};

async function getIcon(name) {
    const result = icons[name] || "M13,14H11V10H13M13,18H11V16H13M1,21H23L12,2L1,21Z";
    
    if (result.path || result.viewBox) return result;

    return { path: result };
}

window.customIconsets = window.customIconsets || {};
window.customIconsets["mdx"] = getIcon;
