// Inicializar CodeMirror en el primer textarea
var editedCodeEditor = CodeMirror.fromTextArea(document.getElementById("edited_code"), {
    mode: "text/x-java",
    theme: "midnight",
    lineNumbers: true,
    styleActiveLine: true, // Enable line highlighting on hover
});


CodeMirror.defineMode("custom-tresdir", function () { // custom style for code mirror

    return {
        startState: function () {
        return { inString: false };
        },
        token: function (stream, state) {
        if (stream.eatSpace()) return null;

        // Resaltar palabras clave
        if (stream.match(/(START|END|RETURN|ON)\b/)) {
            return "keyword-red";
        }

        // Resaltar palabras clave
        if (stream.match(/(ASSIGN|NEW|SUM|MULT|SUB|DIV|LTH|LEQ|GEQ|GTH|BWNOT|ISVOID|PARAM|CALL)\b/)) {
            return "keyword-green";
        }

        // Resaltar palabras bool
        if (stream.match(/(true|false)\b/)) {
            return "keyword-bool";
        }

        // Resaltar palabras string
        if (stream.match(/'[^']*'/)) {
            return "keyword-string";
        }

        // Resaltar palabras int
        if (stream.match(/\b\d+\b/)) {
            return "keyword-int";
        }

        // Resaltar palabras que comienzan con "CL|L|MT|S" y pueden contener cualquier carácter
        if (stream.match(/\b(CL|L|MT)\w*|S\d+\b/)) {
            return "custom-tag";
        }

        // Resaltar temporales
        if (stream.match(/\bt\d+\b/)) {
            return "custom-temp";
        }

        // Cambiar el color de las palabras no resaltadas
        if (stream.match(/\b\w+\b/)) {
            return "custom-base";
        }

        // Otros tokens
        stream.next();
        return null;
        }
    };
});

// Configura CodeMirror con el nuevo modo de resaltado de sintaxis
var tresdirEditor = CodeMirror.fromTextArea(document.getElementById("tresdir"), {
    mode: "custom-tresdir", // Utiliza el nuevo modo personalizado
    theme: "midnight",
    lineNumbers: true,
    styleActiveLine: true,
});