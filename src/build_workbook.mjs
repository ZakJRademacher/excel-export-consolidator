import {execFileSync} from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
// Layout builds are intentionally separate from the canonical native Excel file.
// Native Power Query integration must be completed and validated in Excel.
const output=path.join(root,'layout-build');
const result=JSON.parse(await fs.readFile(path.join(root,'evidence/reference-results.json'),'utf8'));
const wb=Workbook.create();
const sheets=Object.fromEntries(['Summary','Start here','Clean master','Needs review','Import history','Query source'].map(n=>[n,wb.worksheets.add(n)]));
const navy='#23354D', ink='#253548', muted='#64748B', light='#EEF2F6', amber='#FFF0C2';
for(const sheet of Object.values(sheets)){
  sheet.showGridLines=false;
  sheet.getRange('A1:K35').format.font={name:'Arial',size:11,color:ink};
  sheet.getRange('A1:A35').format.columnWidth=3;
  sheet.getRange('B2').values=[[sheet.name==='Summary'?'Export consolidation':sheet.name]];
  sheet.getRange('B2').format.font={name:'Arial',size:16,bold:true,color:navy};
  sheet.getRange('B3:H3').format.borders={bottom:{style:'thin',color:'#B9C4D0'}};
  sheet.getRange('B4:H4').format.rowHeight=12;
  sheet.getRange('B1:K35').format.verticalAlignment='center';
}
function header(s,range){s.getRange(range).format={fill:navy,font:{name:'Arial',size:11,color:'#FFFFFF',bold:true},rowHeight:27,horizontalAlignment:'center',verticalAlignment:'center',borders:{insideVertical:{style:'thin',color:'#FFFFFF'}}};}
function details(name,headers,rows,widths){
  const s=sheets[name], end=String.fromCharCode(65+headers.length-1), last=6+rows.length;
  s.getRange('A2').values=[[name]];
  s.getRange('B2').clear({applyTo:'contents'});
  s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
  s.getRange('A3:'+end+'3').format.borders={bottom:{style:'thin',color:'#B9C4D0'}};
  s.getRange('A6:'+end+'6').values=[headers];header(s,'A6:'+end+'6');
  if(rows.length)s.getRange('A7:'+end+last).values=rows;
  s.getRange('A7:'+end+Math.max(last,7)).format.font={name:'Arial',size:11,color:ink};
  s.getRange('A7:'+end+Math.max(last,7)).format.rowHeight=21;
  widths.forEach((w,i)=>s.getRangeByIndexes(0,i,Math.max(last,35),1).format.columnWidth=w);
  s.freezePanes.freezeRows(6);
  return s;
}
const cleanFields=['RowID','OrderID','OrderDate','ShipDate','Category','Region','ProductID','Sales','SourceFile','SourceRow'];
const cleanRows=result.rows.filter(r=>r.Status==='Clean').map(r=>cleanFields.map(k=>['OrderDate','ShipDate'].includes(k)?new Date(r[k]+'T00:00:00Z'):k==='Sales'?Number(r[k]):r[k]));
const master=details('Clean master',cleanFields,cleanRows,[11,23,16,16,23,14,25,18,32,13]);
master.getRange('A4').values=[['Accepted records only. RowID is unique; source row means logical CSV record, with the header counted as 1.']];
master.getRange('C7:D'+(6+cleanRows.length)).setNumberFormat('mm/dd/yyyy');
master.getRange('H7:H'+(6+cleanRows.length)).setNumberFormat('#,##0.0000');
master.getRange('H7:J'+(6+cleanRows.length)).format.horizontalAlignment='right';
const reviewFields=['Status','RowID','Reason','SourceFile','SourceRow','RawOrderDate','RawSales','Action','RawRecord'];
const reviewRows=result.rows.filter(r=>r.Status!=='Clean').map(r=>reviewFields.map(k=>k==='Action'?(r.Status==='Repeat skipped'?'No action unless repeat was intentional':r.Status==='File issue'?'Check filename profile, headers and CSV structure':'Correct source record, save CSV, then Refresh All'):r[k]));
const review=details('Needs review',reviewFields,reviewRows,[21,11,62,32,13,20,16,58,90]);
review.getRange('A4').values=[['Filter Status to Needs review or File issue for action. Repeat skipped rows document excluded identical copies.']];
review.getRange('A7:A1006').conditionalFormats.add('containsText',{text:'Needs review',format:{fill:'#FFF0C2',font:{color:'#805218',bold:true}}});
review.getRange('A7:A1006').conditionalFormats.add('containsText',{text:'File issue',format:{fill:'#FCE7E7',font:{color:'#9B3030',bold:true}}});
const logFields=['SourceFile','InputRows','CleanRows','ReviewRows','RepeatedRows','FileIssues','LastRefresh','SourceFolder'];
const folder=path.join(root,'data/incoming').replaceAll('\\','/');
const stamp=new Date();
const logs=result.files.map(f=>logFields.map(k=>k==='LastRefresh'?stamp:k==='SourceFolder'?folder:f[k]));
const log=details('Import history',logFields,logs,[32,16,16,16,18,15,25,95]);
log.getRange('A4').values=[['Current folder snapshot, replaced on refresh. File issues have unknown row counts and remain visible separately.']];
log.getRange('G7:G'+(6+logs.length)).setNumberFormat('mm/dd/yyyy hh:mm');
const setup=sheets['Start here']; setup.getRange('B1:H50').format.columnWidth=17;
setup.getRange('B5').values=[['1. Set the source folder below. Retain every CSV that belongs in the current master.']];
setup.getRange('B7').values=[['Folder']];setup.getRange('B8').values=[[folder]];
setup.getRange('B8').format={fill:amber,font:{name:'Arial',size:11,color:ink},wrapText:true,rowHeight:58};
setup.getRange('B1:B50').format.columnWidth=38;setup.getRange('C1:C50').format.columnWidth=25;
setup.tables.add('B7:B8',true,'ImportSettings');
setup.getRange('B10').values=[['2. Select Data > Refresh All. Wait for all queries to finish without errors.']];
setup.getRange('B12').values=[['3. Check Summary, correct source errors listed in Needs review, then refresh again.']];
setup.getRange('B14').values=[['Generated output tables are replaced on refresh. Make corrections in the source CSVs.']];
setup.getRange('B16').values=[['Recognized column names']];setup.getRange('E16').values=[['File parsing profiles']];
const profiles=[['Prefix','Delimiter','DateFormat','Culture'],['batch_a_',',','yyyy-MM-dd','en-US'],['batch_b_',',','MM/dd/yyyy','en-US'],['batch_c_',';','dd/MM/yyyy','en-US'],['batch_d_',',','yyyy-MM-dd','en-US'],['batch_e_',',','yyyy-MM-dd','en-US']];
const aliases=[['Alias','Canonical'],...cleanFields.slice(0,8).map(x=>[x,x]),...[
['Line ID','RowID'],['Order Ref','OrderID'],['Placed On','OrderDate'],['Shipped On','ShipDate'],['Product Group','Category'],['Sales Region','Region'],['SKU','ProductID'],['Sales Amount','Sales'],
['record_id','RowID'],['order','OrderID'],['order_dt','OrderDate'],['ship_dt','ShipDate'],['dept','Category'],['territory','Region'],['item_code','ProductID'],['amount','Sales']]];
setup.getRange('B18:C'+(17+aliases.length)).values=aliases;
setup.tables.add('B18:C'+(17+aliases.length),true,'ColumnMapping');header(setup,'B18:C18');
setup.getRange('E18:H23').values=profiles;setup.tables.add('E18:H23',true,'FileFormats');header(setup,'E18:H18');
setup.getRange('E1:E50').format.columnWidth=18;setup.getRange('F1:F50').format.columnWidth=14;setup.getRange('G1:G50').format.columnWidth=20;
setup.getRange('E26').values=[['Source: Kaggle Superstore Sales Dataset, Rohit Sahoo (GPL 2 label).']];
setup.getRange('E28').values=[['https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting']];
setup.getRange('E30').values=[['Historical source values with disclosed format variations and seeded defects.']];
setup.getRange('E32').values=[['Amounts use source monetary units. Up to four decimal places are retained.']];
setup.getRange('E34').values=[['No fuzzy matching. Conflicting RowIDs quarantine every copy.']];
setup.getRange('E36').values=[['Close CSV files before refresh. Do not change source files during a refresh.']];
const sum=sheets.Summary;sum.tabColor=navy;setup.tabColor='#647C98';
sum.getRange('B1:B35').format.columnWidth=37;sum.getRange('C1:C35').format.columnWidth=21;sum.getRange('D1:D35').format.columnWidth=4;sum.getRange('E1:E35').format.columnWidth=76;
sum.getRange('B5').values=[['Last loaded']];sum.getRange('C5').formulas=[["=MAX('Import history'!G7:G10006)"]];sum.getRange('C5').setNumberFormat('mm/dd/yyyy hh:mm');
sum.getRange('B7:C7').values=[['Import result','Count']];header(sum,'B7:C7');
const metrics=[['Files loaded',"=COUNTA('Import history'!A7:A10006)",'Each CSV has one import-history row.'],['Rows parsed',"=SUM('Import history'!B7:B10006)",'File issues have unknown counts. Review them separately.'],['Clean master rows',"=SUM('Import history'!C7:C10006)",'Unique accepted records, available on Clean master.'],['Rows needing correction',"=SUM('Import history'!D7:D10006)",'Correct the source records listed in Needs review.'],['Identical repeats skipped',"=SUM('Import history'!E7:E10006)",'Identical records were counted once in the master.'],['Files needing correction',"=SUM('Import history'!F7:F10006)",'Fix the file format or mapping before using a complete total.']];
metrics.forEach((r,i)=>{const n=i+8;sum.getRange('B'+n).values=[[r[0]]];sum.getRange('C'+n).formulas=[[r[1]]];sum.getRange('E'+n).values=[[r[2]]];});
sum.getRange('B8:C13').format.rowHeight=28;sum.getRange('C8:C13').setNumberFormat('#,##0');sum.getRange('C8:C13').format.horizontalAlignment='right';
sum.getRange('C11').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0,format:{fill:amber,font:{bold:true,color:'#805218'}}});
sum.getRange('C13').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0,format:{fill:'#FCE7E7',font:{bold:true,color:'#9B3030'}}});
sum.getRange('B16').values=[['Accepted sales (source units)']];sum.getRange('C16').formulas=[["=SUM('Clean master'!H7:H100006)"]];sum.getRange('C16').setNumberFormat('#,##0.0000');sum.getRange('C16').format.horizontalAlignment='right';
sum.getRange('B18').values=[['Next action']];sum.getRange('C18').formulas=[['=IF(C13>0,"Fix file errors first",IF(C11>0,"Review flagged records",IF(C10=0,"No accepted records","Check query status before use")))']];sum.getRange('C18').format.font={name:'Arial',size:11,bold:true,color:navy};
sum.getRange('B21').values=[['How to read this result']];sum.getRange('B21').format.font={name:'Arial',size:11,bold:true,color:navy};
sum.getRange('B23').values=[['Start with rows needing correction and files needing correction.']];
sum.getRange('B25').values=[['Use Clean master for the accepted records. Needs review explains excluded records.']];
sum.getRange('B27').values=[['Open Start here to set the folder, check mappings, and refresh.']];
sum.getRange('B29').values=[['A failed refresh can leave old results visible. Check Excel query errors and Last loaded.']];
sum.getRange('B31').values=[['This sample contains deliberately seeded issues. Details are in docs/SAMPLE.md.']];
const qs=sheets['Query source'];
qs.getRange('B5').values=[['Power Query source. The same code is supplied as individual files in power-query/.']];
qs.getRange('B7:C7').values=[['Query','M source']];header(qs,'B7:C7');
for(const [i,name] of ['Consolidation','CleanMaster','NeedsReview','ImportHistory'].entries()){
 qs.getRange('B'+(8+i)+':C'+(8+i)).values=[[name,await fs.readFile(path.join(root,'power-query',name+'.pq'),'utf8')]];
}
qs.getRange('B1:B15').format.columnWidth=24;qs.getRange('C1:C15').format.columnWidth=100;
qs.getRange('C8:C11').format={wrapText:false,rowHeight:23};
wb.recalculate();
const inspection=await wb.inspect({kind:'table',range:'Summary!B5:E18',include:'values,formulas',tableMaxRows:14,tableMaxCols:4,maxChars:3500});
await fs.writeFile(path.join(root,'evidence/workbook-inspection.ndjson'),inspection.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2000});
await fs.writeFile(path.join(root,'evidence/formula-scan.ndjson'),errors.ndjson);
await fs.mkdir(output,{recursive:true});
for(const [name,range] of [['Summary','B2:H32'],['Start here','B2:H43'],['Clean master','A2:J17'],['Needs review','A2:H17'],['Import history','A2:G13']]){
 const preview=await wb.render({sheetName:name,range,scale:1.4,format:'png'});
 await fs.writeFile(path.join(root,'evidence',name.toLowerCase().replaceAll(' ','-')+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(output,'Export Consolidator.xlsx'));
execFileSync(process.env.PYTHON || 'python', [path.join(root,'src/normalize_workbook.py'), path.join(output,'Export Consolidator.xlsx')]);
console.log(JSON.stringify({file:path.join(output,'Export Consolidator.xlsx'),metrics:result.metrics}));

