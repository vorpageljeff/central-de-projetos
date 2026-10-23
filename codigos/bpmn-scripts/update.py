from pathlib import Path
p=Path('work/deck/build.mjs')
s=p.read_text()
a=s.index("s=slide('Caso 1:")
b=s.index("s=slide('Caso 2:",a)
s=s[:a]+'''s=slide('Exemplo BPMN: aprovação de compra','Solicitante, gestor e Compras participam do mesmo processo',`Exemplo didático autoral. Leia o fluxo seguindo os conectores. A necessidade identificada inicia o processo. O solicitante registra a solicitação. O gestor avalia necessidade e orçamento. O gateway exclusivo escolhe um caminho conforme o resultado da avaliação. Se aprovar, Compras efetua a compra e o processo termina com compra realizada. Se recusar, o solicitante recebe a justificativa e o processo termina com solicitação recusada. Todos pertencem à mesma empresa, representada pela pool. As lanes organizam as responsabilidades. O fluxo de sequência pode cruzar as lanes. O gateway encaminha o resultado da avaliação, não executa a análise. Simplificação: toda compra exige aprovação e não há falhas na execução.`,['silver','omg']);
function box(g,x,y,w,h,fill='none',lw=2){return s.shapes.add({geometry:g,position:{left:x,top:y,width:w,height:h},fill,line:{fill:C.ink,width:lw}});}
box('rect',66,218,1148,366);box('rect',66,218,140,122);box('rect',66,340,140,122);box('rect',66,462,140,122);
text(s,'Solicitante',78,264,120,35,21,true);text(s,'Gestor',78,386,120,35,21,true);text(s,'Compras',78,508,120,35,21,true);
const st=box('ellipse',239,262,36,36,'#FFFFFF');
const request=box('roundRect',320,250,168,60,'#EFF8F6');text(s,'Registrar\\nsolicitação',330,257,148,50,21);
const review=box('roundRect',530,371,172,62,'#EFF8F6');text(s,'Avaliar necessidade\\ne orçamento',537,380,158,50,19);
const gw=box('diamond',753,375,54,54,'#FFF2CF');text(s,'X',770,388,25,30,22);text(s,'Compra aprovada?',720,342,205,30,20,true);
const no=box('roundRect',916,250,164,60,'#EFF8F6');text(s,'Receber justificativa\\nda recusa',924,258,150,50,19);
const yes=box('roundRect',916,493,164,60,'#EFF8F6');text(s,'Efetuar compra',926,510,147,32,20);
const en=box('ellipse',1142,262,36,36,'#FFFFFF',4);const ey=box('ellipse',1142,505,36,36,'#FFFFFF',4);
function link(a,b,f='right',t='left',kind='elbow'){s.shapes.connect(a,b,{fromSide:f,toSide:t,kind,line:{fill:C.ink,width:2},head:{type:'triangle',width:'sm',length:'sm'}});}
link(st,request);link(request,review);link(review,gw);link(gw,no,'top','left');link(gw,yes,'bottom','left');link(no,en);link(yes,ey);
text(s,'Não',851,277,58,28,20,true);text(s,'Sim',850,523,58,28,20,true);
text(s,'Necessidade',216,305,110,25,16);text(s,'Recusada',1120,310,90,25,16);text(s,'Realizada',1120,550,90,25,16);
text(s,'O losango com X seleciona um caminho. As raias mostram quem executa cada tarefa.',66,615,1148,42,24,true,C.accent);
''' +s[b:]
s=s.replace("finalPath:root+'/outputs/Aula_BPMN_10_slides.pptx'","finalPath:root+'/outputs/Aula_BPMN_10_slides_com_exemplo.pptx'")
Path('work/deck/build_updated.mjs').write_text(s)
