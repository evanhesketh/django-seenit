"use strict";

const POST_CONTAINERS = document.getElementsByClassName("post-container");
const UP_VOTE = document.getElementsByClassName("upvote");
const DOWN_VOTE = document.getElementsByClassName("downvote");
const REPLY_BTN = document.getElementsByClassName("reply-btn");
const BASE_URL = "http://localhost:8000";

async function upVote(target) {
  const id = target.getAttribute("data-id");
  const postType = target.getAttribute("data-posttype");
  const ratingElement = target.nextElementSibling;

  try {
    await axios.post(`${BASE_URL}/api/v1/upvote`, { id: id, type: postType });
    let rating = +ratingElement.innerText;
    rating++;
    ratingElement.textContent = rating;
  } catch (err) {
    console.log("Error:", err);
  }
}

async function downVote(target) {
  const id = target.getAttribute("data-id");
  const postType = target.getAttribute("data-posttype");
  const ratingElement = target.previousElementSibling;

  try {
    await axios.post(`${BASE_URL}/api/v1/downvote`, { id: id, type: postType });
    let rating = +ratingElement.innerText;
    rating--;
    ratingElement.textContent = rating;
  } catch (err) {
    console.log("Error:", err);
  }
}

function addVoteClickHandlers() {
  for (let elem of POST_CONTAINERS) {
    elem.addEventListener("click", async function (evt) {
      const upVoteTarget = evt.target.closest(".upvote");
      const downVoteTarget = evt.target.closest(".downvote");

      if (upVoteTarget) {
        upVote(upVoteTarget);
      }

      if (downVoteTarget) {
        downVote(downVoteTarget);
      }
    });
  }
}

function addReplyClickHandler() {
  for (let elem of REPLY_BTN) {
    elem.addEventListener("click", function (evt) {
      const replyForm = evt.target.nextElementSibling;
      if (replyForm.style.display === "none") {
        replyForm.style.display = "block";
      } else {
        replyForm.style.display = "none";
      }
    });
  }
}

window.addEventListener("load", function () {
  addVoteClickHandlers();
  addReplyClickHandler();
});
