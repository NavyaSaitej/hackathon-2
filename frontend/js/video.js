/**
 * QuickCards — Video Module
 *
 * Manages the YouTube iframe embed using the privacy-enhanced
 * youtube-nocookie.com domain. Handles PiP collapse/expand and
 * timestamp seeking via postMessage.
 */

let _currentVideoId = null;

const iframe = document.getElementById("yt-iframe");
const wrapper = document.getElementById("video-wrapper");
const toggleBtn = document.getElementById("btn-toggle-video");
const titleText = document.getElementById("video-title-text");

/**
 * Load a YouTube video into the iframe.
 * @param {string} videoId - The 11-character YouTube video ID
 * @param {string} [title] - Optional display title
 */
export function loadVideo(videoId, title = "Video") {
  _currentVideoId = videoId;
  iframe.src = `https://www.youtube-nocookie.com/embed/${videoId}?enablejsapi=1&rel=0`;
  titleText.textContent = title;

  // Ensure video is expanded
  wrapper.classList.remove("collapsed");
  toggleBtn.querySelector("i").className = "fa-solid fa-chevron-up";
}

/**
 * Seek the embedded video to a specific timestamp.
 * Uses the YouTube iframe postMessage API.
 * @param {number} seconds - Timestamp in seconds
 */
export function seekTo(seconds) {
  if (!iframe.src) return;

  // Expand video if collapsed
  if (wrapper.classList.contains("collapsed")) {
    wrapper.classList.remove("collapsed");
    toggleBtn.querySelector("i").className = "fa-solid fa-chevron-up";
  }

  // YouTube iframe API postMessage command
  iframe.contentWindow.postMessage(
    JSON.stringify({
      event: "command",
      func: "seekTo",
      args: [seconds, true],
    }),
    "*",
  );
}

/**
 * Clear the video and reset the panel.
 */
export function clearVideo() {
  iframe.src = "";
  _currentVideoId = null;
  titleText.textContent = "Video";
}

// Toggle collapse/expand
toggleBtn.addEventListener("click", () => {
  const isCollapsed = wrapper.classList.toggle("collapsed");
  toggleBtn.querySelector("i").className = isCollapsed
    ? "fa-solid fa-chevron-down"
    : "fa-solid fa-chevron-up";
});
