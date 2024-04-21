console.log("+-------+-------+-------+-------+-------+");
console.log("|  for  |   my  | love  | your  | shape |");
console.log("|-------+-------+-------+-------+-------|");
console.log("|       |  word |       |       |rotator|");
console.log("|-------+-------+-------+-------+-------|");
console.log("|       |  cel  |       |       |       |");
console.log("+-------+-------+-------+-------+-------+");

var userId; // used for logging primarily

// key DOM elements we need to be updating
const gameBoard = document.getElementById('game-board');
const scoreDiv = document.getElementById('score');
const msgDiv = document.getElementById('messages');
var go4itbtn = document.getElementById("go4broke");
var currentInputDiv;
var oldInputDiv ;

// colors and keyboard CONSTANTS
const KEYBD_STANDARD = "standard";
const KEYBD_VIRTUAL = "virtual";
const COOKIE_INSTR = "wordcel-instr";
const COOKIE_KEYBD = "wordcel-keyboard";
const CORRECT = '#44cc44'; // correct answer
const NEUTRAL = '#ffffff'; // neutral
const INCORRECT = '#ff2222'; // incorrect answer
const scoreColors = [ // not really used anymore
    '#555555',
    '#555555',
    '#555555',
    '#555555',
    '#555555',
    '#555555',
];

// board size, this pretty much needs to be 3 at this point.
const NUM_ROWS = 3;

// scoring system
const STARTING_POINTS = 80;
const POINTS_PER_HINT = 10;
var hintsClicked = 0;
var secondsUsed = 0;
var numberCorrect = 0;
var wrongAnswers = 0; // may not be needed anymore
var keyboardMode = KEYBD_VIRTUAL; // STANDARD; // VIRTUAL;
var youlost = false;
var feedbackSteps = 0;

//
// Set up the Game Data, use the date to get today's puzzle
// 
var dt = new Date();
const options = { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' };
// secret url parameter lets you look days into the future to see tomorrow's game
// ?dt=1 tomorrow
// ?dt=2 two days out, etc.
const urlParams = new URLSearchParams(window.location.search);
var daysAhead = 0;
if (urlParams.get('dt')) { daysAhead = urlParams.get('dt') * 60 * 60 * 1000 * 24; }
dt = new Date(dt.getTime() + daysAhead);
const formattedDate = dt.toLocaleDateString('en-US', options);
const daysSinceEpoch = Math.floor(dt / 8.64e7);
//console.log("days since 1/1/70 is" + daysSinceEpoch);
var gameData = JSON.parse(jsonData);
var totalGames = gameData.length;
var gameNumber = (daysSinceEpoch - 19833) % totalGames; // roll over when we reach the end
var thisGame = gameData[gameNumber]; // today's game data
var sets = [];
var hints = [];
var lastSetNum = -1;
var setNum = -1;
for (let i = 0; i < NUM_ROWS; i++) {
    //console.log( "row["+i+"].c=",thisGame.rows[0].c );
    sets[i] = thisGame.rows[i].c;
    hints[i] = thisGame.rows[i].h;
    lastSetNum = setNum
}

var minWidth = -100; // for sizing all the text properly, this will be the default div width

// go for it and game clock
var postGo4It = false;
var timerRunning = false;
let timerId = null;

function computePoints() {
    return STARTING_POINTS - POINTS_PER_HINT * hintsClicked - secondsUsed;
}
// as soon as everything is fully loaded, this will get called
window.onload = function () {
    // Function to get a cookie by name
    userId = getCookie('wordcel');

    // Check if the 'wordcel' cookie exists
    if (!userId) {
        // Cookie not found, so generate a new UUID
        userId = generateUUID();
    }

    // Set or update the cookie with the userId for 365 days
    setCookie('wordcel', userId, 365); // This will either set a new cookie or update the existing one's expiration date
    log("Started");
    // Ensure you have the setCookie() function correctly implemented to handle the expiration
};


function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}


// Example implementation of the setCookie function
function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function setWords() {
    // fill divs for each word
    for (let rowIndex = 0; rowIndex < NUM_ROWS; rowIndex++) {
        row = sets[rowIndex];
        for (let colIndex = 0; colIndex < 5; colIndex++) {
            const word = row[colIndex];
            const div = document.getElementById(rowIndex + "." + (colIndex));
            div.dataset.wordValue = word;
            // Set innerText for 0th, 2nd, and 4th divs

            if (colIndex === 0 || colIndex === 2 || colIndex === 4) { div.innerText = word; }
        }
    }
}
function enableStandardKeyboard() {
    //console.log("enable standard keyboard");
    document.getElementById('keyboard').style.display = 'none';
    document.addEventListener('click', clickOnDocument);
    document.addEventListener('focus', clickOnDocument);
    for (let rowIndex = 0; rowIndex < NUM_ROWS; rowIndex++) {
        row = sets[rowIndex];
        for (let colIndex = 0; colIndex < 5; colIndex++) {
            const div = document.getElementById(rowIndex + "." + (colIndex));
            // Set innerText for 0th, 2nd, and 4th divs

            if (colIndex === 0 || colIndex === 2 || colIndex === 4) { ; }
            else {
                div.contentEditable = true; // Allow user to type into the div
                div.addEventListener('keydown', handleStandardUserInput);
                div.addEventListener('blur', handleStandardUserInput);
                div.addEventListener('focus', handleStandardUserInput);
            }
        }
    }
}

function enableVirtualKeyboard() {
    //console.log( "enable virtual keyboard");
    document.getElementById('keyboard').style.display='block';
    document.addEventListener('keydown', clickOnActualKey);
    document.addEventListener('click', clickOnDocument);

    for (let rowIndex = 0; rowIndex < NUM_ROWS; rowIndex++) {
        row = sets[rowIndex];
        for (let colIndex = 0; colIndex < 5; colIndex++) {
            const div = document.getElementById(rowIndex + "." + (colIndex));
            if (colIndex === 0 || colIndex === 2 || colIndex === 4) { ; }
            else {
                //div.contentEditable = true; // Allow user to type into the div
                //div.addEventListener('keypress', handleVirtualUserInput);
                div.addEventListener('blur', handleVirtualUserInput);
                div.addEventListener('click', handleVirtualUserInput);
                div.addEventListener('touchstart', handleVirtualUserInput, { passive: false });
            }
        }
    }

    // "keyboard" click event handling
    document.querySelectorAll('.key, .key2').forEach(img => {
        img.addEventListener('click', clickOnVirtualKey);
    });

}

// Function to create the game board
function createGameBoard() {
    go4itbtn.addEventListener('click', clickGoForBroke);
    // this next listener is a bit odd, it's needed because you can be in an editable div
    // and press tab and its possible the next div the tab key will take you to
    // is the goforbroke button. if we add other clickable buttons they could end
    // up in here too. we just need to make sure when that happens that we reset
    // the div you just left so it no longer is outlined, that's really all this is for.
    go4itbtn.addEventListener('focus', clickOnDocument);
    msgDiv.innerHTML = "";
    updateScore();
    setWords();

    // decide which keyboard to show
    // if there is a cookie, honor it
    // if there isn't a cookie, use virtual keyboard on small screens and standard on large.
    var keyb = getCookie(COOKIE_KEYBD);
    if (!keyb || keyb === "") {
        //console.log("no cookie, let's decide based on screen size");
        if (screen.width < 768) { keyboardMode = KEYBD_VIRTUAL;  }
        else { keyboardMode = KEYBD_STANDARD;  }
        // we don't set a cookie here, we only do that if the user interacts with the gear
        // and is explicit about it. //setCookie(COOKIE_KEYBD, keyboardMode);
    }
    else {
        //console.log("has cookie it is " + keyb);
        keyboardMode = keyb;
    }
    
    if( keyboardMode === KEYBD_STANDARD) { enableStandardKeyboard(); } 
    else { enableVirtualKeyboard(); }

    // Click event handling
    document.querySelectorAll('.btn').forEach(img => {
        img.addEventListener('click', clickOnHint);
    });

    // Touch event handling, this is more complicated so that we prevent
    // a single touch on the screen from firing multiple calls to swap
    document.querySelectorAll('.btn').forEach(img => {
        let touchInProgress = false; // Flag to track touch state
        let debounceTimer = null; // Timer for debounce mechanism

        //console.log( "2)adding event listener on ", img )
        const touchOnHint = function (event) {
            event.preventDefault(); // Prevent default touch behavior
            const divId = this.parentNode.id;
            swap(divId);
        };

        img.addEventListener('touchstart', function (event) {
            if (!touchInProgress && event.touches.length === 1) {
                touchInProgress = true; // Set touch in progress

                // If there's a debounce timer, clear it
                if (debounceTimer !== null) {
                    clearTimeout(debounceTimer);
                    debounceTimer = null;
                }

                // Execute touchOnHint after a short delay
                debounceTimer = setTimeout(() => {
                    touchOnHint.call(this, event);
                    debounceTimer = null; // Reset debounce timer
                }, 300); // Adjust the delay as needed
            }
        }, { passive: true });

        img.addEventListener('touchend', function () {
            touchInProgress = false; // Reset touch state when touch ends

            // If there's a debounce timer, clear it
            if (debounceTimer !== null) {
                clearTimeout(debounceTimer);
                debounceTimer = null;
            }
        });

    });

    // did they signal to skip instructions?
    var inst = getCookie(COOKIE_INSTR);
    if (inst == "no-mas") { startGame(); }
}

function clickOnActualKey(event) {
    if (!currentInputDiv) { return; }
    var k = event.key.toLowerCase();
    if (k === "backspace") { k = "del"; }
    if (k === "enter" || k === "return" || k === "tab") {
        leaveDiv();
        return;
    }
    var key = document.getElementById(k);
    if (key) { clickOnKey(k); }
}

function clickOnVirtualKey(event) {
    if (!currentInputDiv) { return; }
    else { clickOnKey(event.target.id); }
    event.stopPropagation();
}
function clickOnKey(key) {
    if ('vibrate' in navigator) {
        navigator.vibrate(10); // Vibrate for 50 milliseconds on key up
    }
    if (key === "enter") {
        leaveDiv();
        return;
    }
    var ct = currentInputDiv.innerText;
    if (!ct) { ct = ""; }
    if (key == "del") {
        if (ct.length > 0) { ct = ct.substring(0, ct.length - 1); }
        else { ; } // do nothing, it's already empty
    }
    else { ct = ct + key; }
    currentInputDiv.innerText = ct;
}

function clickOnHint(event) {
    var divId = event.target.id;
    divId = divId.replace("img.", "");
    event.target.remove(); // remove the image
    revealHint(divId); // put the hint text in the div and show it
    hintsClicked += 1;
}

function clickGoForBroke() {
    var inst = getCookie('g4bi');
    if( inst != "0" ) { 
        gameBoard.style.opacity = 0.33;
        var div = document.getElementById("go4bhelp");
        div.style.display="flex";
    } else { 
        goForBroke() ;
    }
}
function dontGoForBroke() {
    var div = document.getElementById("go4bhelp");
    div.style.display = "none";
    gameBoard.style.opacity = 1.0;
}

function goForBroke() {
    log("Go4Broke");
    var inst = document.getElementById("go4bInstCheckbox");
    if (inst.checked) { setCookie("g4bi", "0", 365); }
    var div = document.getElementById("go4bhelp");
    div.style.display = "none";
    gameBoard.style.opacity= 1.0;

    msgDiv.innerText = computePoints() + " points left";
    scoreDiv.style.display = 'none';
    go4itbtn.style.display = 'none';

    // yes i'm an idiot who numbered from 0 on rows and 1 on columns
    for (r = 0; r < 3; r++) {
        for (c = 1; c < 5; c++) {
            // if div r,1 is correct don't show hint 1 or 2
            // if div r,3 is correct don't show hint 3 or 4
            const div1 = document.getElementById(r + '.1');
            const div3 = document.getElementById(r + '.3');
            if (c < 3) {
                const correctWord = div1.dataset.wordValue.toLowerCase();
                var typedWord = div1.innerText.trim().toLowerCase().replace(/<div><br><\/div>/g, "");
                if (typedWord != correctWord) {
                    //console.log(" --- show hint " + r + "," + c + " " + hints[r][c]);
                    showHint(r, c, hints[r][c - 1]);
                }
            }
            else {
                const correctWord = div3.dataset.wordValue.toLowerCase();
                var typedWord = div3.innerText.trim().toLowerCase().replace(/<div><br><\/div>/g, "");
                if (typedWord != correctWord) {
                    //console.log(" --- show hint " + r + "," + c + " " + hints[r][c]);
                    showHint(r, c, hints[r][c - 1]);
                }
            }
        }
    }
    postGo4It = true;
    startTimer();
}
function greyAll() {
    //console.log("in greyAll()");
    for (var i = 0; i < 3; i++) {
        greyPlus(i + '.first');
        greyPlus(i + '.last');
    }
}
function greyPlus(id) {
    const img = document.getElementById('img.' + id);
    if (img) {
        if (img.src.endsWith('greenPlus.png')) {
            //unopenedHints--;
            //console.log("img."+id + " score= " + score + " unopenedHints=" + unopenedHints);
            img.src = 'greyPlus.png';
            img.removeEventListener('click', clickOnHint);
        }
        //else { console.log( "nope, cuz img.src=" + img.src ) ; }
    }
}
function revealHint(id) {
    if (score == 0) { return; } // score=0 means you don't get any more hints, so stop now

    const row = id.split(".")[0];
    const part = id.split(".")[1];

    var col = 2;
    if (part == 'last') { showHint(row, 3, hints[row][2]); }
    else { showHint(row, 2, hints[row][1]); }
    greyPlus(id);
    score--;
    if (score == 0) { greyAll(); }

    updateScore();
}
function colorAllGreen() {
    for (let r = 0; r < NUM_ROWS; r++) {
        for (let c = 1; c < 4; c++) {
            if (c == 1 || c == 3) {
                const div = document.getElementById(r + "." + c);
                div.style.backgroundColor = CORRECT;
            }
        }
    }
}
function getAssociatedHint(div) {
    var hintBtnId = div.id;
    hintBtnId = hintBtnId.replace('.1', '.first');
    hintBtnId = hintBtnId.replace('.3', '.last');
    hintBtnId = "img." + hintBtnId;
    return document.getElementById(hintBtnId);
}
function clickOnDocument(event) {
    if( keyboardMode === KEYBD_VIRTUAL) { leaveDiv(); }
    else { handleStandardUserInput(event) ; }
}

function leaveDiv(event) {
    if (!currentInputDiv) { return; }
    oldInputDiv = currentInputDiv;
    oldInputDiv.style.border = "1px solid black";
    var oldHintBtn = getAssociatedHint(oldInputDiv);
    if (oldHintBtn) { oldHintBtn.style.opacity = 0.0; }

    const correctWord = oldInputDiv.dataset.wordValue.toLowerCase();
    var typedWord = oldInputDiv.innerText.trim().toLowerCase().replace(/<div><br><\/div>/g, "");

    // Check if typed word matches the correct word
    if (typedWord === correctWord) {
        oldInputDiv.style.backgroundColor = CORRECT; // green
        oldInputDiv.innerText = typedWord; // the 'trim' and so on may be needed
        oldInputDiv.removeEventListener('blur', handleVirtualUserInput);
        oldInputDiv.removeEventListener('click', handleVirtualUserInput);
        oldInputDiv.removeEventListener('touchstart', handleVirtualUserInput);
        //const cell = oldInputDiv.id.split('.');
        //if (cell[1] == 1) { greyPlus(cell[0] + ".first"); }
        //else { greyPlus(cell[0] + ".last"); }
    } else if (typedWord === null || typedWord.length === 0 || typedWord === "") {
        oldInputDiv.style.backgroundColor = NEUTRAL; // no text in the div, white
    }
    else {
        oldInputDiv.style.backgroundColor = INCORRECT;
    }
    properlySizeText(currentInputDiv);
    updateScore();
    if (event) { event.stopPropagation(); }
    currentInputDiv = null;
}

function rating(n) { 
    log( "Rating_" + n ) ; 
    document.getElementById("thumbsUp").style.display="none";
    document.getElementById("thumbsDown").style.display = "none";
    feedbackSteps++;
    if (feedbackSteps == 2) { document.getElementById("feedback").style.display = "none"; }
}
function sendFeedback() { 
    var msg = document.getElementById('commentInput').value; 
    log("Feedback_" + msg); 
    document.getElementById("commentInput").style.display = "none";
    document.getElementById("sendFeedback").style.display = "none";
    feedbackSteps++;
    if( feedbackSteps == 2) { document.getElementById("feedback").style.display = "none"; }
}

// Event listener for input changes
function handleVirtualUserInput(event) {
    if (numberCorrect == 6) { return; }
    if (currentInputDiv && event.target != currentInputDiv) {
        leaveDiv(event);
    }
    currentInputDiv = event.target; // set the div we are now updating
    currentInputDiv.style.backgroundColor = NEUTRAL;
    currentInputDiv.style.border = "2px dashed blue";
    var hintBtn = getAssociatedHint(currentInputDiv);
    if (hintBtn) { hintBtn.style.opacity = 1.0; } // make the button visible if it still exists
    event.stopPropagation();
}

function handleStandardUserInput(event) {
    if (numberCorrect == 6) { return; }
    currentInputDiv = event.target;
    
    // clean up the div we just left
    if( oldInputDiv && oldInputDiv != currentInputDiv ) {
        oldInputDiv.style.border = "1px solid black";
        var hintBtn = getAssociatedHint(oldInputDiv);
        if (hintBtn) { hintBtn.style.opacity = 0.0; }
    }
    
    var correctWord = currentInputDiv.dataset.wordValue ;
    if( correctWord ) { correctWord = correctWord.toLowerCase(); }
    var typedWord = currentInputDiv.innerText ;
    if( typedWord ) { typedWord = typedWord.trim().toLowerCase().replace(/<div><br><\/div>/g, ""); }

    // Check if Enter key is pressed
    if (event.key === 'Enter' || event.key === 'Return' || event.type === 'blur' || event.key === 'Tab') {
        //console.log("detected enter/return/blur in " + currentInputDiv.id );
       
        // Check if typed word matches the correct word
        if (typedWord === correctWord) {
            currentInputDiv.style.backgroundColor = CORRECT; // green
            currentInputDiv.innerText = typedWord.trim().toLowerCase(); // the 'trim' and so on may be needed
            currentInputDiv.contentEditable = false; // don't allow user to type into the div
            currentInputDiv.removeEventListener('keydown',handleStandardUserInput);
            currentInputDiv.removeEventListener('blur', handleStandardUserInput);
            currentInputDiv.style.border = "1px solid black";
            var hintBtn = getAssociatedHint(currentInputDiv);
            if (hintBtn) { hintBtn.style.opacity = 0.0; }
        } else if (typedWord === null || typedWord.length === 0 || typedWord === "") {
            currentInputDiv.style.backgroundColor = NEUTRAL; // no text in the div, white
        }
        else {
            currentInputDiv.style.backgroundColor = INCORRECT;
        }
        properlySizeText(currentInputDiv);
        updateScore();
    } else {
        if (currentInputDiv.className.indexOf("word")>=0 && typedWord != correctWord) {
            currentInputDiv.style.border = "2px dashed blue";
            currentInputDiv.style.outline = "none";
            var hintBtn = getAssociatedHint(currentInputDiv);
            if (hintBtn) { hintBtn.style.opacity = 1.0; }
            currentInputDiv.style.backgroundColor = NEUTRAL; // no text in the div, white
            oldInputDiv = currentInputDiv;
        }
    }
}

function showHint(row, col, hint) {
    //console.log("show hint " + row + ", " + col + " = " + hint ) ;
    const id = 'h' + row + '.' + col;
    const c2 = document.getElementById(id);
    c2.innerHTML = hint;
    c2.style.opacity = '1.0';
    if( col == 2 || col == 4 ) { 
        c2.style.alignItems = 'flex-start'; // align to top of div
    }
    //console.log("set opacity of " + c2 + " to 1.0");
    log("Hint");
}

function disableTextEntry() {
    for (let rowIndex = 0; rowIndex < NUM_ROWS; rowIndex++) {
        const row = sets[rowIndex];
        for (let colIndex = 0; colIndex < 5; colIndex++) {
            const word = row[colIndex];
            const div = document.getElementById(rowIndex + "." + colIndex);
            div.contentEditable = false; // Allow user to type into the div
            if( keyboardMode === KEYBD_STANDARD) { 
                div.contentEditable = false; // don't allow user to type into the div
                div.removeEventListener('click',   handleStandardUserInput);
                div.removeEventListener('keydown', handleStandardUserInput);
                div.removeEventListener('blur',    handleStandardUserInput);
                div.removeEventListener('focus',   handleStandardUserInput);
            } else { 
                div.removeEventListener('blur',       handleVirtualUserInput);
                div.removeEventListener('click',      handleVirtualUserInput);
                div.removeEventListener('touchstart', handleVirtualUserInput);
            }
        }
    }
}

function log(msg) {
    var i = document.getElementById("log");
    i.src = "log.png?_" + userId + "_" + msg + "_";
}

function updateScore() {
    numberCorrect = 0;
    // console.log("updatescore");
    // how many correct are there?
    for (let rowIndex = 0; rowIndex < NUM_ROWS; rowIndex++) {
        const div1 = document.getElementById(rowIndex + ".1");
        const div3 = document.getElementById(rowIndex + ".3");
        const div1Text = div1.innerHTML;
        const div3Text = div3.innerHTML;
        if (div1Text != null && div1.dataset.wordValue != null) {
            if (div1Text.trim().toLowerCase().replace(/<div><br><\/div>/g, "")
                == div1.dataset.wordValue.trim().toLowerCase()) {
                numberCorrect++;
            }
        }
        if (div3Text != null && div3.dataset.wordValue != null) {
            if (div3Text.trim().toLowerCase().replace(/<div><br><\/div>/g, "")
                == div3.dataset.wordValue.trim().toLowerCase()) {
                numberCorrect++;
            }
        }
    }
    if (numberCorrect == 6 && !youlost) {
        scoreDiv.style.display = "none";
        go4itbtn.style.display = "none";
        msgDiv.innerText = "You Got It! " + computePoints() + " pts";
        log("Solved");
        stopTimer();
        leaveDiv();
        disableTextEntry();
        colorAllGreen();
        clearInterval(completionCheckInterval);
        showFeedback();
    }
    else {
        if (!postGo4It) {
            var pts = computePoints();
            var pWord = " points";
            scoreDiv.innerText = pts + pWord;
            scoreDiv.style.color = scoreColors[score];
        }
    }
}

function startTimer() {
    // Check if the timer is already running
    if (timerRunning) {
        return; // Exit the function if the timer is already running
    }
    timerRunning = true;
    let timeLeft = computePoints();

    // Update the div content every second
    timerId = setInterval(function () {
        timeLeft--;
        secondsUsed++;
        msgDiv.innerHTML = `${timeLeft} points left`;
        updateScore();
        // When countdown is over
        if (timeLeft <= 0) {
            sorryPanel();
            stopTimer(true); // Call stopTimer with timeUp flag true
        }
    }, 1000);
}

function stopTimer(timeUp = false) {
    clearInterval(timerId);
    timerId = null;
    timerRunning = false;
    go4itbtn.style.display = "none";
}

function nextStep(stepNumber) {
    // Hide current step
    var newId = "step" + stepNumber;
    var oldId = "step" + (stepNumber - 1);
    document.getElementById(oldId).style.display = 'none';  // hide old step
    document.getElementById(newId).style.display = 'block'; // show new step
}


function startGame() {
    // Hide the last step of the instruction wizard
    document.getElementById('step1').style.display = 'none';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('step3').style.display = 'none';

    // see if they checked box for no more instructions
    var checkbox = document.getElementById('instructionCheckbox');
    if (checkbox.checked) { setCookie("wordcel-instr", "no-mas", 365); }

    // Show the game board
    gameBoard.style.display = 'block';

    //console.log("in startGame");

    // get the minimum width of our divs
    for (let r = 0; r < NUM_ROWS; r++) {
        for (let c = 0; c < 5; c++) {
            const div = document.getElementById(r + "." + c);
            if (div) {
                if (div.offsetWidth > minWidth) { minWidth = div.offsetWidth; }
                var style = window.getComputedStyle(div);
                var computedWidth = parseFloat(style.width);
            } else {
                console.log(`ERROR: Div with ID ${r + "." + c} not found.`);
            }
        }
    }
    // if a div is wider than the min, resize the text
    for (let r = 0; r < NUM_ROWS; r++) {
        for (let c = 0; c < 5; c++) {
            const div = document.getElementById(r + "." + c);
            if (div) {
                properlySizeText(div);
            }
        }
    }
}
function sorryPanel() {
    log("Sorry");
    youlost=true;
    gameBoard.style.display = 'none'; // Hide the game board    
    document.getElementById('sorry').style.display = 'block';     // show the sorry message
    var tshirt = document.getElementById('tshirt');
    clearInterval(completionCheckInterval);
    tshirt.classList.add('animate');
}

function revealAnswers() {
    gameBoard.style.display = 'block'; // Hide the sorry panel 
    document.getElementById('sorry').style.display = 'none';     // show the game board
    for (let rowIndex = 0; rowIndex < sets.length; rowIndex++) {
        const row = sets[rowIndex];
        const div1 = document.getElementById(rowIndex + ".1");
        div1.innerHTML = div1.dataset.wordValue;
        const div3 = document.getElementById(rowIndex + ".3");
        div3.innerHTML = div3.dataset.wordValue;

        properlySizeText(div1);
        properlySizeText(div3);
    }
    scoreDiv.style.display = "none";
    go4itbtn.style.display = "none";
    msgDiv.innerText = "Maybe Next Time";
    disableTextEntry();
    showFeedback();
}

function showFeedback() {
    document.getElementById('keyboard').style.display = 'none';
    document.getElementById('feedback').style.display="block";
}

function getWordWidth(text, font) {
    // Create a temporary off-screen canvas element
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    //console.log("text ="+ text + " and font = " + font);
    // Set the font style and size
    context.font = font;

    // Measure the width of the text
    const metrics = context.measureText(text);
    //console.log('Width of the word "' + text + '": ' + metrics.width + ' pixels');
    return metrics.width;
}


function properlySizeText(div) {
    var computedStyle = window.getComputedStyle(div);
    var fontName = computedStyle.fontFamily;
    var fontSize = computedStyle.fontSize;
    var font = fontSize + " " + fontName;
    var safety = 0;
    var text = div.innerText;
    // a div may have multiple lines of text separate by \n, find the line with the widest text
    var textLines = text.split('\n');
    var longestLine = "";
    for (i = 0; i < textLines.length; i++) {
        if (getWordWidth(textLines[i], font) > getWordWidth(longestLine, font)) { longestLine = textLines[i]; }
    }
    //console.log("in properly size text, the text is " + text ) ; 

    while (getWordWidth(longestLine, font) > minWidth) { // used to be +2 > minWidth
        //console.log("current font size is " + fontSize);
        const newFontSizeNumber = parseInt(fontSize) - 2;
        // console.log(longestLine + " new font size is " + newFontSizeNumber);
        div.style.fontSize = newFontSizeNumber + 'px';
        font = newFontSizeNumber + 'px ' + fontName;
        // change the font on the actual div here
        fontSize = newFontSizeNumber;
        if (safety++ > 6) { break; }
    }
}


function randomSort(a, b) {
    return Math.random() - 0.5; // Returns a random value that can be positive or negative
}
// Call the function to create the game board
createGameBoard();
var completionCheckInterval = setInterval(updateScore, 200);


