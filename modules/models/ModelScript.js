function toggleReading(element) {
    var temp = element.getAttribute("rt")
    element.setAttribute("rt",
        element.getElementsByTagName("rt")[0].innerHTML)
    element.getElementsByTagName("rt")[0].innerHTML = temp
}

function toRuby(match, p1, p2, offset, string) {
    return '<ruby rt="' + p2 + '" onmouseover="toggleReading(this)" onmouseout="toggleReading(this)" ' + ' >' +
        p1 + '<rt>&nbsp;</rt>' + '</ruby>'
}

function parseReading(elementId) {
    var text = document.getElementById(elementId).innerHTML
    var rubyParsed = text.replace(/ ?([^ ]+)\[([^ ]+)\] ?/g, toRuby)
    rubyparsed = rubyParsed.replace("\s", function(){return "";})
    document.getElementById(elementId).innerHTML = rubyParsed
}

try {
    document.getElementById("meaning").innerHTML= card["Meaning"]
    document.getElementById("reading").innerHTML= card["Reading"]
    document.getElementById("jisho").setAttribute("href", "http://jisho.org/word/" + card["Expression"])
    document.getElementById("tangorin").setAttribute("href", "http://tangorin.com/general/" + card["Expression"])
    document.getElementById("exampleSentence").innerHTML= card["Example Sentence"]
    document.getElementById("exampleSentenceTranslation").innerHTML= card["Translation"]
    document.getElementById("graphic").innerHTML= card["Graphic"]
    var metadata = JSON.parse(card["Metadata"])
    var table = document.getElementById("kanjiTable")
    var rowKanji = table.insertRow()
    rowKanji.classList.add("kanji")
    for(k in metadata["kanji"]) {
        var cell = rowKanji.insertCell()
        cell.innerHTML="<td><p class='kanji'>"+metadata["kanji"][k]["kanji"]+"</p></td>"
    }
    var rowKeyword = table.insertRow()
    rowKeyword.classList.add("keyword")
    for(k in metadata["kanji"]) {
        var cell = rowKeyword.insertCell()
        cell.innerHTML="<td><p class='keyword'>"+metadata["kanji"][k]["keyword"]+"</p></td>"
    }
    var rowKun = table.insertRow()
    rowKun.classList.add("kunYomi")
    for(k in metadata["kanji"]) {
        var cell = rowKun.insertCell()
        cell.innerHTML="<td><p class='kunYomi'>"+metadata["kanji"][k]["kunYomi"]+"</p></td>"
    }
    var rowOn = table.insertRow()
    rowOn.classList.add("onYomi")
    for(k in metadata["kanji"]) {
        var cell = rowOn.insertCell()
        cell.innerHTML="<td><p class='onYomi'>"+metadata["kanji"][k]["onYomi"]+"</p></td>"
    }
    var rowHeisig = table.insertRow()
    rowHeisig.classList.add("heisigFrame")
    for(k in metadata["kanji"]) {
        var cell = rowHeisig.insertCell()
        cell.innerHTML="<td><p class='heisigFrame'>"+metadata["kanji"][k]["heisigFrame"]+"</p></td>"
    }
    var b = document.getElementById("toggleTable")
    b.onclick  = function() {
        var panel = document.getElementById("liKanjiTable")
        console.log(panel.style.display)
        if (panel.style.display === "") {
            panel.style.display = "inline";
        } else {
            panel.style.display = "";
        }
    }
    parseReading("reading")
    parseReading("exampleSentence")
} catch(err) {
    try {
            document.getElementById("meaning").innerHTML= card["Meaning"]
    }
    catch(err) {}
    try {
            document.getElementById("reading").innerHTML= card["Reading"]
            parseReading("reading")
    }
    catch(err) {}
}
