// ARIS Studio AI - After Effects Auto-Generated ExtendScript
app.beginUndoGroup("ARIS AI Motion Comp");

var project = app.project || app.newProject();
var comp = project.items.addComp("ARIS_Short_1791900498", 1080, 1920, 1, 15, 30);

// Add Dark Ambient Solid Background
var bg = comp.layers.addSolid([0.05, 0.07, 0.12], "Dark Background", 1080, 1920, 1);

// Add Text Layer
var textLayer = comp.layers.addText("Create 9:16 kinetic typography with boun");
var textProp = textLayer.property("Source Text");
var textDoc = textProp.value;
textDoc.fontSize = 72;
textDoc.fillColor = [1, 1, 1];
textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
textProp.setValue(textDoc);

// Center and Animate Scale Bounce
var pos = textLayer.property("Transform").property("Position");
pos.setValue([540.0, 960.0]);

var scale = textLayer.property("Transform").property("Scale");
scale.setValueAtTime(0.0, [0, 0, 100]);
scale.setValueAtTime(0.5, [115, 115, 100]);
scale.setValueAtTime(0.8, [100, 100, 100]);

app.endUndoGroup();
