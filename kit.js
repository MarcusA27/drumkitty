const player = new Audio();
let current = null;

function clear() {
  if (current) {
    current.classList.remove("is-playing");
    current = null;
  }
}

player.addEventListener("ended", clear);
player.addEventListener("error", clear);

const pane = document.querySelector(".samples-pane");
const list = document.querySelector(".samples");

if (pane && list) {
  const syncEnd = () => {
    const atEnd = list.scrollTop + list.clientHeight >= list.scrollHeight - 2;
    pane.classList.toggle("is-at-end", atEnd);
  };
  list.addEventListener("scroll", syncEnd, { passive: true });
  window.addEventListener("resize", syncEnd);
  syncEnd();
}

document.querySelectorAll(".sample").forEach((button) => {
  button.addEventListener("click", () => {
    clear();
    player.src = button.dataset.src;
    player.currentTime = 0;
    player.play();
    button.classList.add("is-playing");
    current = button;
  });
});
