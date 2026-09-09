const pptxgen = require("/home/claude/.npm-global/lib/node_modules/pptxgenjs");
const fs = require("fs");

const D = JSON.parse(fs.readFileSync(__dirname + "/data_for_pptx.json"));
const ASSETS = __dirname + "/assets/";

const NAVY = "12213A", TEAL = "1C7293", ORANGE = "F7931E", BLUE = "0072CE";
const LIGHT = "F7F9FC", TEXT = "1B2436", MUTED = "6B7893", RED = "C0392B";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

function footer(slide, n) {
  slide.addText("Togo Digital Access — Diagnostic télécoms & inclusion numérique", { x: 0.5, y: 7.15, w: 8, h: 0.3, fontSize: 9, color: MUTED });
  slide.addText(`${n} / 10`, { x: 12.4, y: 7.15, w: 0.6, h: 0.3, fontSize: 9, color: MUTED, align: "right" });
}
function sectionTitle(slide, kicker, title) {
  slide.addText(kicker.toUpperCase(), { x: 0.5, y: 0.35, w: 8, h: 0.3, fontSize: 12, color: ORANGE, bold: true, charSpacing: 2 });
  slide.addText(title, { x: 0.5, y: 0.62, w: 12.3, h: 0.7, fontSize: 28, bold: true, color: TEXT, fontFace: "Cambria" });
}

// SLIDE 1 — TITRE
{
  const s = pres.addSlide(); s.background = { color: NAVY };
  s.addShape("ellipse", { x: 10.8, y: -1.5, w: 5, h: 5, fill: { color: TEAL, transparency: 75 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 11.8, y: 4.5, w: 3.2, h: 3.2, fill: { color: ORANGE, transparency: 80 }, line: { type: "none" } });
  s.addText("TOGO AI LAB DATA CHALLENGE · ÉCONOMIE NUMÉRIQUE · DÉFI 1", { x: 0.9, y: 1.3, w: 10, h: 0.4, fontSize: 12.5, color: ORANGE, bold: true, charSpacing: 2 });
  s.addText("Togo Digital Access\nDiagnostic territorial de l'accès aux\ntélécommunications et services numériques", {
    x: 0.9, y: 1.85, w: 11, h: 2.6, fontSize: 36, bold: true, color: "FFFFFF", fontFace: "Cambria", lineSpacingMultiple: 1.1 });
  s.addText("Cartographie des infrastructures, score de priorité territoriale par préfecture, et recommandations d'extension de la connectivité.", {
    x: 0.9, y: 4.7, w: 8.7, h: 0.9, fontSize: 15, color: "CADCFC", lineSpacingMultiple: 1.2 });
  const kpis = [[String(D.totals.agences), "agences télécoms"], [D.totals.mm.toLocaleString("fr-FR"), "agents Mobile Money"], [Math.round(D.totals.pop/1e6*10)/10+"M", "habitants estimés"]];
  let kx = 0.9;
  kpis.forEach(([v,l]) => { s.addText(v, {x:kx,y:6.0,w:3,h:0.6,fontSize:30,bold:true,color:ORANGE,fontFace:"Cambria"}); s.addText(l,{x:kx,y:6.6,w:3,h:0.4,fontSize:12,color:"CADCFC"}); kx+=3.1; });
  footer(s, 1);
}

// SLIDE 2 — CONTEXTE / METHODO
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Contexte", "Objectifs, données et pipeline");
  const objectifs = ["Cartographier agences télécoms (Moov/Togocom/CANAL+) et datacenters",
    "Croiser Mobile Money et densité démographique par préfecture",
    "Estimer la population par préfecture (WorldPop 2020, zonal stats)",
    "Construire un score de priorité territoriale reproductible",
    "Identifier les préfectures à cibler en premier"];
  let oy = 1.75;
  objectifs.forEach(t => { s.addShape("ellipse",{x:0.5,y:oy+0.03,w:0.16,h:0.16,fill:{color:ORANGE},line:{type:"none"}});
    s.addText(t,{x:0.85,y:oy-0.12,w:6.1,h:0.5,fontSize:13.5,color:TEXT,valign:"top"}); oy+=0.72; });
  s.addShape("roundRect",{x:7.2,y:1.65,w:5.6,h:3.9,rectRadius:0.1,fill:{color:"FFFFFF"},line:{color:"E3E8F0",width:1}});
  s.addText("PIPELINE DE DONNÉES (reproductible)",{x:7.55,y:1.85,w:5,h:0.3,fontSize:11,bold:true,color:MUTED,charSpacing:1});
  const steps=["1. check_data.py — vérification des fichiers bruts","2. clean_data.py — nettoyage, dédoublonnage, CRS","3. analyze_data.py — jointures spatiales + WorldPop zonal stats","4. score_priorite.py — score de priorité normalisé","5. app/main.py — dashboard Streamlit interactif"];
  let sy=2.3; steps.forEach(t=>{ s.addText(t,{x:7.55,y:sy,w:5,h:0.4,fontSize:12,color:TEXT}); sy+=0.5; });
  s.addShape("roundRect",{x:7.2,y:5.7,w:5.6,h:1.15,rectRadius:0.08,fill:{color:"FDF1EC"},line:{type:"none"}});
  s.addText("⚠ Limite de données",{x:7.45,y:5.83,w:5,h:0.3,fontSize:11.5,bold:true,color:RED});
  s.addText("CANAL+ : export source vide. OpenCelliD (32 antennes) : échantillon collaboratif, non exhaustif — traité à titre illustratif.",{x:7.45,y:6.1,w:5.1,h:0.7,fontSize:10.5,color:TEXT,lineSpacingMultiple:1.15});
  footer(s,2);
}

// SLIDE 3 — VUE D'ENSEMBLE
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Vue d'ensemble", "Densité de population et implantation des agences");
  s.addImage({ path: ASSETS+"carte_densite_agences.png", x:0.5, y:1.55, w:5.6, h:5.55 });
  const stats=[[String(D.totals.agences),"agences télécoms (Moov+Togocom)",ORANGE],[String(D.totals.dc),"datacenters (tous en région Maritime)",TEAL],[D.totals.pop.toLocaleString("fr-FR"),"habitants estimés (WorldPop 2020)",BLUE]];
  let sy=1.75; stats.forEach(([v,l,c])=>{ s.addShape("roundRect",{x:6.5,y:sy,w:6.3,h:1.1,rectRadius:0.08,fill:{color:"FFFFFF"},line:{color:"E3E8F0",width:1}});
    s.addText(v,{x:6.75,y:sy+0.12,w:2.2,h:0.85,fontSize:26,bold:true,color:c,fontFace:"Cambria",valign:"middle"});
    s.addText(l,{x:9.0,y:sy+0.12,w:3.6,h:0.85,fontSize:13,color:TEXT,valign:"middle"}); sy+=1.3; });
  s.addText("Constat : l'infrastructure physique (agences, 100% des datacenters) se concentre autour de Lomé, la zone la plus densément peuplée. Le reste du territoire — surtout le Nord — reste faiblement équipé.",
    {x:6.5,y:sy+0.15,w:6.3,h:1.6,fontSize:12.5,color:MUTED,italic:true,lineSpacingMultiple:1.25});
  footer(s,3);
}

// SLIDE 4 — SCORE DE PRIORITE (methodologie + carte)
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Méthodologie", "Un score de priorité territoriale par préfecture");
  s.addImage({ path: ASSETS+"carte_priorite.png", x:0.5, y:1.55, w:5.3, h:5.55 });
  s.addShape("roundRect",{x:6.1,y:1.6,w:6.7,h:3.1,rectRadius:0.1,fill:{color:"FFFFFF"},line:{color:"E3E8F0",width:1}});
  s.addText("Formule du score",{x:6.4,y:1.8,w:6,h:0.35,fontSize:14,bold:true,color:TEXT});
  s.addText("Score = 0,40 × Population\n         + 0,40 × Déficit Mobile Money\n         + 0,20 × Déficit Antennes",
    {x:6.4,y:2.25,w:6,h:1.1,fontSize:14,fontFace:"Courier New",color:TEAL});
  s.addText("Indicateurs normalisés (0–1) puis combinés. Population : log1p + normalisation directe. Déficits Mobile Money / Antennes : normalisation inverse (moins de service = score plus élevé).",
    {x:6.4,y:3.35,w:6,h:1.3,fontSize:11.5,color:MUTED,lineSpacingMultiple:1.25});
  const rep=[["Forte","🔴",D.niveau_counts["Forte"]||0],["Moyenne","🟠",D.niveau_counts["Moyenne"]||0],["Faible","🟢",D.niveau_counts["Faible"]||0]];
  let ry=4.85; rep.forEach(([l,e,n])=>{ s.addText(`${e} ${l} : ${n} préfectures / 37`,{x:6.4,y:ry,w:6,h:0.4,fontSize:13,color:TEXT}); ry+=0.45; });
  footer(s,4);
}

// SLIDE 5 — TOP 10 PRIORITE
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Résultats", "Top 10 des préfectures prioritaires");
  s.addImage({ path: ASSETS+"bar_top10_priorite.png", x:0.5, y:1.55, w:6.3, h:5.4 });
  const rows=[[{text:"Préfecture",options:{bold:true,color:"FFFFFF",fill:{color:RED}}},
    {text:"Pop.",options:{bold:true,color:"FFFFFF",fill:{color:RED},align:"right"}},
    {text:"Agents MM",options:{bold:true,color:"FFFFFF",fill:{color:RED},align:"right"}},
    {text:"Antennes",options:{bold:true,color:"FFFFFF",fill:{color:RED},align:"right"}},
    {text:"Score",options:{bold:true,color:"FFFFFF",fill:{color:RED},align:"right"}}]];
  D.top10.forEach((r,i)=>{ const fill=i%2===0?"FFFFFF":"FDF1EC";
    rows.push([{text:r.prefecture,options:{fill:{color:fill},color:TEXT,bold:true}},
      {text:Math.round(parseFloat(r.population_worldpop)).toLocaleString("fr-FR"),options:{fill:{color:fill},color:TEXT,align:"right"}},
      {text:r.agents_mobile_money,options:{fill:{color:fill},color:TEXT,align:"right"}},
      {text:r.antennes_opencellid,options:{fill:{color:fill},color:TEXT,align:"right"}},
      {text:parseFloat(r.score_priorite).toFixed(3),options:{fill:{color:fill},color:TEXT,align:"right"}}]); });
  s.addTable(rows,{x:6.9,y:1.55,w:5.9,h:5.4,fontSize:10,border:{type:"solid",color:"E3E8F0",pt:0.5},autoPage:false,colW:[1.7,1.1,1.2,1.1,0.8]});
  footer(s,5);
}

// SLIDE 6 — MOBILE MONEY
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Services numériques", "Mobile Money : le canal le plus décentralisé");
  s.addImage({ path: ASSETS+"bar_mm_faible.png", x:0.5, y:1.55, w:6.3, h:5.2 });
  s.addText(`Avec ${D.totals.mm.toLocaleString("fr-FR")} agents actifs, le Mobile Money atteint les 5 régions du pays — contrairement aux agences opérateurs, très concentrées. Mais l'écart entre préfectures reste important : les moins dotées cumulent souvent une population significative avec moins de 5 agents pour 10 000 habitants.`,
    {x:7.0,y:1.8,w:5.8,h:2.2,fontSize:13.5,color:TEXT,lineSpacingMultiple:1.3});
  s.addShape("roundRect",{x:7.0,y:4.3,w:5.8,h:2.4,rectRadius:0.08,fill:{color:"FFFFFF"},line:{color:"E3E8F0",width:1}});
  s.addText("💡 Lecture stratégique",{x:7.25,y:4.5,w:5.3,h:0.35,fontSize:13,bold:true,color:TEAL});
  s.addText("Le Mobile Money étant déjà le service le plus répandu, il constitue le levier le plus rapide et le moins coûteux pour étendre l'inclusion financière et numérique dans les préfectures à faible couverture d'agences physiques.",
    {x:7.25,y:4.85,w:5.3,h:1.7,fontSize:12,color:TEXT,lineSpacingMultiple:1.25});
  footer(s,6);
}

// SLIDE 7 — DATACENTERS / RESILIENCE
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Infrastructure numérique", "Datacenters : une concentration à risque");
  s.addShape("roundRect",{x:0.5,y:1.7,w:3.6,h:5.0,rectRadius:0.1,fill:{color:NAVY}});
  s.addText(String(D.totals.dc),{x:0.5,y:2.5,w:3.6,h:1.3,fontSize:72,bold:true,color:ORANGE,align:"center",fontFace:"Cambria"});
  s.addText("datacenters recensés\nsur tout le territoire",{x:0.7,y:3.85,w:3.2,h:0.9,fontSize:14,color:"FFFFFF",align:"center"});
  s.addText("100% localisés dans\nla région Maritime (Lomé)",{x:0.7,y:5.4,w:3.2,h:0.9,fontSize:13,color:"CADCFC",align:"center",italic:true});
  s.addShape("roundRect",{x:4.4,y:1.85,w:8.4,h:2.4,rectRadius:0.08,fill:{color:"FFFFFF"},line:{color:"E3E8F0",width:1}});
  s.addText("Risque de résilience",{x:4.65,y:2.05,w:7.9,h:0.35,fontSize:14,bold:true,color:RED});
  s.addText("La concentration à 100% des capacités d'hébergement de données dans un rayon de quelques kilomètres à Lomé constitue un point de défaillance unique : coupure réseau, catastrophe naturelle, saturation électrique. Aucune redondance régionale n'existe à ce jour, ce qui expose l'ensemble des services numériques nationaux à un risque de disponibilité concentré.",
    {x:4.65,y:2.45,w:7.9,h:1.7,fontSize:12,color:TEXT,lineSpacingMultiple:1.25});
  s.addShape("roundRect",{x:4.4,y:4.45,w:8.4,h:2.25,rectRadius:0.08,fill:{color:"F0F9F4"},line:{type:"none"}});
  s.addText("Piste d'action",{x:4.65,y:4.65,w:7.9,h:0.3,fontSize:13,bold:true,color:"166534"});
  s.addText("Étudier la faisabilité d'une deuxième capacité d'hébergement hors Lomé (ex. Kara ou Sokodé, pôles régionaux secondaires) pour réduire le risque de panne nationale et rapprocher le calcul des usages du Nord du pays.",
    {x:4.65,y:5.0,w:7.9,h:1.5,fontSize:12,color:TEXT,lineSpacingMultiple:1.25});
  footer(s,7);
}

// SLIDE 8 — DASHBOARD
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Livrable", "Le dashboard interactif (Streamlit)");
  const feats=[["🏠 Vue nationale","KPI globaux, classement des préfectures les plus peuplées, répartition des agences par opérateur"],
    ["🗺️ Carte territoriale","Carte choroplèthe interactive (Folium) du niveau de priorité, avec info-bulles par préfecture"],
    ["🏆 Priorités","Classement complet des 37 préfectures par score de priorité, avec tableau détaillé filtrable"],
    ["🔎 Diagnostic","Fiche par préfecture : positionnement vs moyenne nationale sur population, Mobile Money, antennes"],
    ["🎯 Recommandations","Pistes d'action générées automatiquement pour les 5 préfectures les plus prioritaires"]];
  let fy=1.7; feats.forEach(([t,d])=>{ s.addShape("roundRect",{x:0.5,y:fy,w:12.3,h:0.92,rectRadius:0.06,fill:{color:"FFFFFF"},line:{color:"E3E8F0",width:1}});
    s.addText(t,{x:0.75,y:fy+0.08,w:3.3,h:0.75,fontSize:13.5,bold:true,color:TEXT,valign:"middle"});
    s.addText(d,{x:4.1,y:fy+0.08,w:8.5,h:0.75,fontSize:12,color:MUTED,valign:"middle"}); fy+=1.05; });
  footer(s,8);
}

// SLIDE 9 — RECOMMANDATIONS
{
  const s = pres.addSlide(); s.background = { color: LIGHT };
  sectionTitle(s, "Recommandations", "Priorités stratégiques d'extension");
  const recos=[["1","Cibler les préfectures en priorité Forte (21/37)","Blitta, Dankpen, Haho, Tchamba et Zio en premier — fort déficit combiné population/Mobile Money/antennes."],
    ["2","Accélérer le déploiement Mobile Money","C'est le canal déjà le plus décentralisé : l'étendre coûte moins cher que d'ouvrir de nouvelles agences physiques."],
    ["3","Diversifier la localisation des datacenters","Réduire le risque de panne nationale en créant une capacité redondante hors de la région Maritime."],
    ["4","Compléter la donnée de couverture réseau","33 antennes recensées est trop faible pour cartographier fiablement les zones blanches ; nouer un partenariat opérateurs/ARCEP."],
    ["5","Institutionnaliser le score de priorité","L'utiliser comme outil de présélection avant audits terrain et arbitrages d'investissement, mis à jour périodiquement."]];
  let ry=1.7; recos.forEach(([n,t,d])=>{ s.addShape("ellipse",{x:0.5,y:ry,w:0.55,h:0.55,fill:{color:ORANGE},line:{type:"none"}});
    s.addText(n,{x:0.5,y:ry,w:0.55,h:0.55,fontSize:20,bold:true,color:"FFFFFF",align:"center",valign:"middle",fontFace:"Cambria"});
    s.addText(t,{x:1.3,y:ry-0.03,w:11.4,h:0.35,fontSize:15.5,bold:true,color:TEXT});
    s.addText(d,{x:1.3,y:ry+0.32,w:11.4,h:0.5,fontSize:12,color:MUTED,lineSpacingMultiple:1.15}); ry+=1.02; });
  footer(s,9);
}

// SLIDE 10 — CONCLUSION
{
  const s = pres.addSlide(); s.background = { color: NAVY };
  s.addShape("ellipse",{x:-1.5,y:5.5,w:5,h:5,fill:{color:TEAL,transparency:78},line:{type:"none"}});
  s.addText("CONCLUSION",{x:0.9,y:0.7,w:8,h:0.4,fontSize:13,color:ORANGE,bold:true,charSpacing:3});
  s.addText("Une fracture numérique nette entre Lomé\net le reste du territoire",{x:0.9,y:1.15,w:11,h:1.3,fontSize:30,bold:true,color:"FFFFFF",fontFace:"Cambria",lineSpacingMultiple:1.1});
  const summary=["L'infrastructure télécom et numérique togolaise reste très centralisée sur la région Maritime (Lomé) : agences, datacenters et, dans une moindre mesure, Mobile Money.",
    "Le Mobile Money est le service le plus décentralisé et le levier d'inclusion numérique le plus rapide à activer.",
    "21 préfectures sur 37 (score de priorité 'Forte') doivent être la cible prioritaire des futurs investissements, en tête desquelles Blitta, Dankpen et Haho."];
  let cy=2.85; summary.forEach(t=>{ s.addShape("rect",{x:0.9,y:cy+0.05,w:0.05,h:0.5,fill:{color:ORANGE},line:{type:"none"}});
    s.addText(t,{x:1.15,y:cy-0.05,w:10.6,h:0.75,fontSize:14,color:"E8ECF4",lineSpacingMultiple:1.2}); cy+=0.95; });
  s.addText("Limites méthodologiques : agences CANAL+ indisponibles ; échantillon d'antennes cellulaires (33 pts) trop réduit pour une carte de couverture radio fiable ; population estimée par imagerie satellite (WorldPop 2020).",
    {x:0.9,y:6.55,w:11.2,h:0.6,fontSize:10.5,italic:true,color:"93A0BD"});
  footer(s,10);
}

pres.writeFile({ fileName: __dirname + "/Togo_Digital_Access_Rapport.pptx" }).then(()=>console.log("PPTX généré"));
