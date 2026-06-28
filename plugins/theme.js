const customTheme = document.createElement('dom-module');
customTheme.register('lumine-review-theme');

Gerrit.install(plugin => {
  // Header color
  const style = document.createElement('style');
  style.innerHTML = `
    :root {
      --header-background-color: #d0318b;
      --header-text-color: #fff;
    }
  `;
  document.head.appendChild(style);

  // Header title with logo
  const domHook = plugin.hook('header-title', {replace: true});
  domHook.onAttached(function(element) {
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
    const div = document.createElement('div');
    div.style.cssText = 'display:flex; align-items:center; gap:8px;';
    div.innerHTML = `
      <img src="/static/logo.png" style="height:32px;" alt="LumineDroid" />
      <span class="titleText">LumineDroid&nbsp;</span>
    `;
    element.appendChild(div);
  });

  // Mobile header title
  const mobileHook = plugin.hook('header-mobile-title', {replace: true});
  mobileHook.onAttached(function(element) {
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
    const div = document.createElement('div');
    div.style.cssText = 'display:flex; align-items:center; gap:8px;';
    div.innerHTML = `
      <img src="/static/logo.png" style="height:32px;" alt="LumineDroid" />
      <span class="titleText">LumineDroid&nbsp;</span>
    `;
    element.appendChild(div);
  });
});
