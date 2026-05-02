const MAX_BOOKS = 1000000;
const state = {
  secret: 573892,
  binarySteps: [],
  currentBinaryIndex: -1,
  autoTimer: null
};

const quizQuestions = [
  {
    question: "If you check every book one by one, what is it called?",
    options: ["Brute force", "Binary search", "Painting"],
    answer: "Brute force"
  },
  {
    question: "Binary search works by:",
    options: ["Checking the middle and cutting half", "Closing your eyes", "Checking randomly"],
    answer: "Checking the middle and cutting half"
  },
  {
    question: "Time complexity means:",
    options: ["How steps grow when the problem grows", "How colorful the app is", "How loud the sound is"],
    answer: "How steps grow when the problem grows"
  }
];

document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page === "level-one") {
    initLevelOne();
  }
});

function initLevelOne() {
  const form = document.getElementById("gameControls");
  const randomButton = document.getElementById("randomNumberButton");
  const resetButton = document.getElementById("resetButton");
  const nextButton = document.getElementById("nextStepButton");
  const autoButton = document.getElementById("autoPlayButton");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    setSecretNumber();
  });
  randomButton.addEventListener("click", generateRandomNumber);
  resetButton.addEventListener("click", resetGame);
  nextButton.addEventListener("click", nextBinaryStep);
  autoButton.addEventListener("click", autoPlayBinarySearch);

  renderComparisonTable();
  renderQuiz();
  resetGame();
}

function setSecretNumber() {
  const input = document.getElementById("secretNumber");
  const value = Number.parseInt(input.value.replace(/,/g, ""), 10);

  if (!Number.isInteger(value) || value < 1 || value > MAX_BOOKS) {
    setFeedback("Please choose a friendly number from 1 to 1,000,000.");
    input.focus();
    return;
  }

  state.secret = value;
  input.value = String(value);
  clearAutoPlay();
  simulateBruteForce();
  startBinarySearch();
  setFeedback(`Secret book ${formatNumber(value)} is ready. Try stepping through binary search.`);
}

function generateRandomNumber() {
  const random = Math.floor(Math.random() * MAX_BOOKS) + 1;
  document.getElementById("secretNumber").value = String(random);
  setSecretNumber();
}

function resetGame() {
  clearAutoPlay();
  state.secret = 573892;
  state.binarySteps = [];
  state.currentBinaryIndex = -1;

  const input = document.getElementById("secretNumber");
  input.value = String(state.secret);
  document.getElementById("bruteTrail").innerHTML = "";
  document.getElementById("bruteSteps").textContent = "-";
  document.getElementById("bruteProgress").style.width = "0%";
  document.getElementById("binaryBubbles").innerHTML = "";
  document.getElementById("binarySteps").textContent = "Around 20 or fewer";
  renderRangeBar(1, MAX_BOOKS);
  setFeedback("Pick a secret book, then start the game.");
}

function simulateBruteForce() {
  const trail = document.getElementById("bruteTrail");
  const progress = document.getElementById("bruteProgress");
  const steps = document.getElementById("bruteSteps");
  const firstChecks = [1, 2, 3, 4, 5];

  trail.innerHTML = "";
  firstChecks.forEach((number, index) => {
    const chip = document.createElement("span");
    chip.className = "check-chip";
    chip.textContent = number;
    chip.style.animationDelay = `${index * 80}ms`;
    trail.appendChild(chip);
  });

  const ellipsis = document.createElement("span");
  ellipsis.className = "check-chip";
  ellipsis.textContent = "...";
  trail.appendChild(ellipsis);

  const found = document.createElement("span");
  found.className = "check-chip";
  found.textContent = formatNumber(state.secret);
  trail.appendChild(found);

  steps.textContent = `${formatNumber(state.secret)} checks`;
  progress.style.width = `${Math.max(2, Math.min(100, (state.secret / MAX_BOOKS) * 100))}%`;
}

function startBinarySearch() {
  state.binarySteps = getBinarySearchSteps(state.secret, 1, MAX_BOOKS);
  state.currentBinaryIndex = -1;
  document.getElementById("binaryBubbles").innerHTML = "";
  document.getElementById("binarySteps").textContent = "Ready in around 20 or fewer steps";
  renderRangeBar(1, MAX_BOOKS);
}

function getBinarySearchSteps(secret, min, max) {
  const steps = [];
  let low = min;
  let high = max;

  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    let direction = "found";
    let nextLow = low;
    let nextHigh = high;

    if (mid < secret) {
      direction = "higher";
      nextLow = mid + 1;
    } else if (mid > secret) {
      direction = "lower";
      nextHigh = mid - 1;
    }

    steps.push({ low, high, mid, direction, nextLow, nextHigh });

    if (mid === secret) {
      break;
    }

    low = nextLow;
    high = nextHigh;
  }

  return steps;
}

function renderBinaryStep() {
  const bubbles = document.getElementById("binaryBubbles");
  bubbles.innerHTML = "";

  state.binarySteps.slice(0, state.currentBinaryIndex + 1).forEach((step, index) => {
    const chip = document.createElement("span");
    chip.className = `binary-chip${index === state.currentBinaryIndex ? " active" : ""}`;
    chip.textContent = formatNumber(step.mid);
    bubbles.appendChild(chip);
  });

  const step = state.binarySteps[state.currentBinaryIndex];
  if (!step) {
    renderRangeBar(1, MAX_BOOKS);
    return;
  }

  renderRangeBar(step.low, step.high);

  if (step.direction === "found") {
    document.getElementById("binarySteps").textContent = `Found in only ${state.currentBinaryIndex + 1} steps`;
    setFeedback(`Found it in only ${state.currentBinaryIndex + 1} steps! Smart work beats hard work!`);
    showCelebration();
    clearAutoPlay();
  } else {
    const hint = step.direction === "higher" ? "The secret is higher, so keep the right half." : "The secret is lower, so keep the left half.";
    document.getElementById("binarySteps").textContent = `${state.currentBinaryIndex + 1} step${state.currentBinaryIndex === 0 ? "" : "s"} so far`;
    setFeedback(`Checked ${formatNumber(step.mid)}. ${hint}`);
  }
}

function nextBinaryStep() {
  if (!state.binarySteps.length) {
    setSecretNumber();
    return;
  }

  if (state.currentBinaryIndex >= state.binarySteps.length - 1) {
    setFeedback("The secret book is already found. Reset or try another number.");
    return;
  }

  state.currentBinaryIndex += 1;
  renderBinaryStep();
}

function autoPlayBinarySearch() {
  if (!state.binarySteps.length) {
    setSecretNumber();
  }

  clearAutoPlay();
  nextBinaryStep();
  state.autoTimer = window.setInterval(() => {
    if (state.currentBinaryIndex >= state.binarySteps.length - 1) {
      clearAutoPlay();
      return;
    }
    nextBinaryStep();
  }, 650);
}

function renderRangeBar(low, high) {
  const keep = document.getElementById("rangeKeep");
  const lowLabel = document.getElementById("rangeLow");
  const highLabel = document.getElementById("rangeHigh");
  const startPercent = ((low - 1) / MAX_BOOKS) * 100;
  const widthPercent = ((high - low + 1) / MAX_BOOKS) * 100;

  lowLabel.textContent = formatNumber(low);
  highLabel.textContent = formatNumber(high);
  keep.style.marginLeft = `${Math.max(0, startPercent)}%`;
  keep.style.width = `${Math.max(0.5, widthPercent)}%`;
}

function showCelebration() {
  const layer = document.getElementById("confettiLayer");
  const pieces = ["🎉", "⭐", "✨", "🚀", "📚"];
  layer.innerHTML = "";

  for (let index = 0; index < 22; index += 1) {
    const piece = document.createElement("span");
    piece.className = "confetti-piece";
    piece.textContent = pieces[index % pieces.length];
    piece.style.left = `${Math.random() * 96}%`;
    piece.style.animationDelay = `${Math.random() * 220}ms`;
    layer.appendChild(piece);
  }

  window.setTimeout(() => {
    layer.innerHTML = "";
  }, 1700);
}

function renderComparisonTable() {
  const rows = [
    { size: "10 books", brute: "10", binary: "4" },
    { size: "100 books", brute: "100", binary: "7" },
    { size: "1,000 books", brute: "1,000", binary: "10" },
    { size: "1,000,000 books", brute: "1,000,000", binary: "20" }
  ];
  const table = document.getElementById("comparisonTable");

  table.innerHTML = `
    <div class="compare-row compare-head">
      <div class="compare-cell">Problem size</div>
      <div class="compare-cell">Brute force</div>
      <div class="compare-cell">Binary search</div>
    </div>
  `;

  rows.forEach((row) => {
    table.insertAdjacentHTML("beforeend", `
      <div class="compare-row">
        <div class="compare-cell" data-label="Problem size">${row.size}</div>
        <div class="compare-cell" data-label="Brute force">${row.brute} steps</div>
        <div class="compare-cell" data-label="Binary search">${row.binary} steps</div>
      </div>
    `);
  });
}

function checkQuizAnswer(button, correctAnswer) {
  const quizCard = button.closest(".quiz-card");
  const buttons = quizCard.querySelectorAll(".quiz-option");
  const isCorrect = button.textContent === correctAnswer;

  buttons.forEach((option) => {
    option.classList.remove("correct", "wrong");
  });
  button.classList.add(isCorrect ? "correct" : "wrong");
  document.getElementById("quizFeedback").textContent = isCorrect ? "Great job!" : "Try again!";

  if (isCorrect) {
    showCelebration();
  }
}

function renderQuiz() {
  const list = document.getElementById("quizList");
  list.innerHTML = "";

  quizQuestions.forEach((quiz, index) => {
    const card = document.createElement("article");
    card.className = "quiz-card";

    const title = document.createElement("h3");
    title.textContent = `Question ${index + 1}`;
    const prompt = document.createElement("p");
    prompt.textContent = quiz.question;
    const options = document.createElement("div");
    options.className = "quiz-options";

    quiz.options.forEach((optionText) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "quiz-option";
      button.textContent = optionText;
      button.addEventListener("click", () => checkQuizAnswer(button, quiz.answer));
      options.appendChild(button);
    });

    card.append(title, prompt, options);
    list.appendChild(card);
  });
}

function setFeedback(message) {
  document.getElementById("gameFeedback").textContent = message;
}

function clearAutoPlay() {
  if (state.autoTimer) {
    window.clearInterval(state.autoTimer);
    state.autoTimer = null;
  }
}

function formatNumber(number) {
  return new Intl.NumberFormat("en-US").format(number);
}
