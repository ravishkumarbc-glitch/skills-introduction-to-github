// Confirm before destructive actions
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      const msg = form.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // Show chosen file name and drag-and-drop highlight
  const fileInput = document.getElementById("file-input");
  const dropZone = document.getElementById("drop-zone");
  const fileChosen = document.getElementById("file-chosen");

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const name = fileInput.files[0]?.name;
      if (name) {
        fileChosen.textContent = `Selected: ${name}`;
        fileChosen.classList.remove("hidden");
      } else {
        fileChosen.classList.add("hidden");
      }
    });
  }

  if (dropZone && fileInput) {
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
    ["dragleave", "dragend"].forEach((evt) =>
      dropZone.addEventListener(evt, () => dropZone.classList.remove("dragover"))
    );
    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        const name = fileInput.files[0]?.name;
        if (name) {
          fileChosen.textContent = `Selected: ${name}`;
          fileChosen.classList.remove("hidden");
        }
      }
    });
  }
});
