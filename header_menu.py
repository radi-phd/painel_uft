"""Keep Streamlit's native sidebar control aligned with the sticky header."""

import inspect

import streamlit as st
import streamlit.components.v1 as components

#arquvio para manter o botão de abrir a barra lateral alinhado com o cabeçalho fixo. 
#função align_sidebar_open_button() é chamada dentro de pai.py
def align_sidebar_open_button():
    """Install one observer in the parent page; call inside the header container."""
    html = """
<script>
(() => {
  // Streamlit renders this component in a same-origin iframe. The actual
  // sidebar button and the sticky header both belong to the parent document.
  const host = window.parent;
  const doc = host.document;
  if (window.frameElement) window.frameElement.setAttribute("tabindex", "-1");
  const name = "__uftHeaderMenuAlignment";
  if (host[name]) host[name].dispose();

  let frame = 0;
  let observedHeader = null;
  let observedButton = null;
  let buttonOriginalStyle = null;
  const resizeObserver = host.ResizeObserver ? new host.ResizeObserver(schedule) : null;

  function restoreButton() {
    if (!observedButton || !buttonOriginalStyle) return;
    for (const property of ["position", "top", "left"]) {
      const original = buttonOriginalStyle[property];
      if (original.value) {
        observedButton.style.setProperty(property, original.value, original.priority);
      } else {
        observedButton.style.removeProperty(property);
      }
    }
  }

  function update() {
    frame = 0;
    const marker = doc.querySelector(".uft-header-marker");
    const header = marker && marker.closest(
      '[data-testid="stLayoutWrapper"], [data-testid="stVerticalBlockBorderWrapper"]'
    );
    const button = doc.querySelector(
      '[data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"] button'
    );

    if (header !== observedHeader) {
      if (observedHeader && resizeObserver) resizeObserver.unobserve(observedHeader);
      observedHeader = header;
      if (observedHeader && resizeObserver) resizeObserver.observe(observedHeader);
    }
    if (button !== observedButton) {
      if (observedButton && resizeObserver) resizeObserver.unobserve(observedButton);
      restoreButton();
      observedButton = button;
      buttonOriginalStyle = button ? Object.fromEntries(
        ["position", "top", "left"].map(property => [property, {
          value: button.style.getPropertyValue(property),
          priority: button.style.getPropertyPriority(property),
        }])
      ) : null;
      if (observedButton && resizeObserver) resizeObserver.observe(observedButton);
    }
    if (!header || !button) return;

    const headerRect = header.getBoundingClientRect();
    const buttonRect = button.getBoundingClientRect();
    if (!headerRect.height || !buttonRect.height) return;
    const top = headerRect.top + (headerRect.height - buttonRect.height) / 2;
    button.style.setProperty("position", "fixed", "important");
    button.style.setProperty("top", `${top}px`, "important");
    button.style.setProperty("left", `${Math.max(0, headerRect.left + 4)}px`, "important");
  }

  function schedule() {
    if (!frame) frame = host.requestAnimationFrame(update);
  }

  const observer = new host.MutationObserver(schedule);
  observer.observe(doc.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["aria-expanded"],
  });
  doc.addEventListener("scroll", schedule, true);
  host.addEventListener("resize", schedule);

  const controller = {
    dispose() {
      observer.disconnect();
      if (resizeObserver) resizeObserver.disconnect();
      doc.removeEventListener("scroll", schedule, true);
      host.removeEventListener("resize", schedule);
      if (frame) host.cancelAnimationFrame(frame);
      restoreButton();
      if (host[name] === controller) delete host[name];
    },
  };
  host[name] = controller;
  window.addEventListener("pagehide", () => {
    if (host[name] === controller) controller.dispose();
  }, {once: true});
  schedule();
})();
</script>
"""
    if hasattr(st, "iframe") and "tab_index" in inspect.signature(st.iframe).parameters:
        # Newer versions require a positive size; one pixel keeps it invisible.
        st.iframe(html, height=1, width=1, tab_index=-1)
    else:
        components.html(html, height=0, width=0)
