/* Light/dark theme switch for the PHY-2105 site.
   Loaded in <head> so the theme is set before the page paints. */
(function () {
    var KEY = 'phy2105-theme', root = document.documentElement, saved = null;
    try { saved = localStorage.getItem(KEY); } catch (e) {}
    root.setAttribute('data-theme', saved || 'light');      // light unless the visitor picked dark

    function addButton() {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'theme-toggle';
        var sync = function () {
            var light = root.getAttribute('data-theme') === 'light';
            b.textContent = light ? '🌙' : '☀️';
            b.title = b.ariaLabel = light ? 'Switch to dark theme' : 'Switch to light theme';
        };
        b.addEventListener('click', function () {
            var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            root.setAttribute('data-theme', next);
            try { localStorage.setItem(KEY, next); } catch (e) {}
            sync();
        });
        sync();
        document.body.appendChild(b);
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', addButton);
    else addButton();
})();
