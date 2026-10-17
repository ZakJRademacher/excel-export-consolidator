let
    Settings = Excel.CurrentWorkbook(){[Name="ImportSettings"]}[Content],
    Folder = Text.Trim(Text.From(Settings{0}[Folder])),
    Mapping = Excel.CurrentWorkbook(){[Name="ColumnMapping"]}[Content],
    Formats = Excel.CurrentWorkbook(){[Name="FileFormats"]}[Content],
    Fields = {"RowID","OrderID","OrderDate","ShipDate","Category","Region","ProductID","Sales"},
    Trim = (x as any) as text => if x = null then "" else Text.Trim(Text.From(x)),
    Key = (x as any) as text => Text.Lower(Text.Remove(Trim(x), {" ","_","-"})),
    Aliases = List.Transform(Mapping[Alias], each Key(_)),
    Canonicals = Mapping[Canonical],
    CheckMap = if List.Count(List.Distinct(Aliases)) <> List.Count(Aliases) then error "Duplicate column aliases in ColumnMapping" else true,
    EmptyRows = #table(Fields & {"SourceFile","SourceRow","Status","Reason","RawOrderDate","RawSales","RawRecord"}, {}),
    Digits = (s as text) as logical => Text.Length(s) > 0 and Text.Select(s,{"0".."9"}) = s,
    Amount = (s as text) as nullable number =>
        let
            Decimals = Text.Split(s,"."),
            Whole = Text.Split(Decimals{0},","),
            ValidWhole = if List.Count(Whole) = 1 then Digits(Whole{0}) else
                Digits(Whole{0}) and Text.Length(Whole{0}) <= 3 and List.AllTrue(List.Transform(List.Skip(Whole), each Digits(_) and Text.Length(_) = 3)),
            Valid = List.Count(Decimals) <= 2 and ValidWhole and
                (if List.Count(Decimals) = 2 then Digits(Decimals{1}) and Text.Length(Decimals{1}) <= 4 else true),
            Parsed = if Valid then try Currency.From(Number.FromText(Text.Remove(s, {","}), "en-US")) otherwise null else null
        in Parsed,
    DateValue = (s as text, fmt as text) as nullable date =>
        let d = try Date.FromText(s,[Format=fmt,Culture="en-US"]) otherwise null
        in if d = null then null else if Date.ToText(d,[Format=fmt,Culture="en-US"]) = s then d else null,
    Label = (s as text, allowed as list) as nullable text =>
        let matches = List.Select(allowed, each Text.Lower(_) = Text.Lower(s))
        in if List.Count(matches) = 1 then matches{0} else null,
    LoadFile = (f as record) as record =>
        let
            Profiles = Table.SelectRows(Formats, each Text.StartsWith(Text.Lower(f[Name]),Text.Lower(Trim([Prefix])))),
            Profile = if Table.RowCount(Profiles) <> 1 then error "File needs exactly one matching format profile" else Profiles{0},
            CultureCheck = if Profile[Culture] <> "en-US" then error "Only en-US numeric culture is supported" else true,
            Source = if CultureCheck then Csv.Document(f[Content],[Delimiter=Profile[Delimiter],Encoding=65001,QuoteStyle=QuoteStyle.Csv,ExtraValues=ExtraValues.Error]) else error "Invalid culture",
            Header = if Table.RowCount(Source) = 0 then error "File is empty; include a header row" else List.Transform(Record.FieldValues(Source{0}), each Trim(_)),
            Names = List.Transform(Header, each let i=List.PositionOf(Aliases, Key(_)) in if i < 0 then "__UNKNOWN__" else Canonicals{i}),
            ValidSchema = List.Count(Names) = 8 and List.Count(List.Distinct(Names)) = 8 and List.Count(List.Difference(Fields,Names)) = 0,
            Body = if ValidSchema then Table.RenameColumns(Table.Skip(Source,1),List.Zip({Table.ColumnNames(Source),Names})) else error "Missing, extra or duplicate mapped columns",
            Numbered = Table.AddIndexColumn(Body,"SourceRow",2,1,Int64.Type),
            Converted = List.Transform(Table.ToRecords(Numbered), (r) =>
                let
                    Raw = Record.SelectFields(r,Fields),
                    Clean = Record.TransformFields(Raw,List.Transform(Fields, each {_, Trim})),
                    OrderDate = DateValue(Clean[OrderDate],Profile[DateFormat]),
                    ShipDate = DateValue(Clean[ShipDate],Profile[DateFormat]),
                    Category = Label(Clean[Category],{"Furniture","Office Supplies","Technology"}),
                    Region = Label(Clean[Region],{"Central","East","South","West"}),
                    Sales = Amount(Clean[Sales]),
                    Issues = List.RemoveNulls({
                        if Clean[RowID] = "" then "Missing RowID" else null,
                        if Clean[OrderID] = "" then "Missing OrderID" else null,
                        if Clean[ProductID] = "" then "Missing ProductID" else null,
                        if OrderDate = null then "Invalid OrderDate" else null,
                        if ShipDate = null then "Invalid ShipDate" else null,
                        if OrderDate <> null and ShipDate <> null then if ShipDate < OrderDate then "ShipDate precedes OrderDate" else null else null,
                        if Category = null then "Invalid Category" else null,
                        if Region = null then "Invalid Region" else null,
                        if Sales = null then "Invalid Sales" else null}),
                    Normal = [RowID=Clean[RowID],OrderID=Clean[OrderID],OrderDate=OrderDate,ShipDate=ShipDate,
                        Category=if Category=null then Clean[Category] else Category,Region=if Region=null then Clean[Region] else Region,
                        ProductID=Clean[ProductID],Sales=Sales],
                    Fingerprint = Text.FromBinary(Json.FromValue(Record.ToList(Normal)),TextEncoding.Utf8)
                in Record.Combine({Normal,[SourceFile=f[Name],SourceRow=r[SourceRow],Issues=Issues,Fingerprint=Fingerprint,
                    GroupKey=if Clean[RowID]="" then "MISSING:" & f[Name] & ":" & Text.From(r[SourceRow]) else "ID:" & Clean[RowID],
                    RawOrderDate=Trim(Raw[OrderDate]),RawSales=Trim(Raw[Sales]),
                    RawRecord=Text.FromBinary(Json.FromValue(Raw),TextEncoding.Utf8)]})),
            Rows = if List.Count(Converted)=0 then #table(Fields & {"SourceFile","SourceRow","Issues","Fingerprint","GroupKey","RawOrderDate","RawSales","RawRecord"},{}) else Table.FromRecords(Converted),
            Forced = Table.Buffer(Rows)
        // Force the table inside try's scope; an unevaluated record can hide errors.
        in if Table.RowCount(Forced) >= 0 then [Rows=Forced,Count=Table.RowCount(Forced)] else error "Unable to evaluate file",
    SourceFiles = if CheckMap then Table.SelectRows(Folder.Contents(Folder), each Text.Lower([Extension])=".csv" and not Text.StartsWith([Name],".") and not Text.StartsWith([Name],"~") and [Attributes]?[Hidden]? <> true) else error "Invalid mapping",
    SortedFiles = Table.Sort(SourceFiles,{{"Name",Order.Ascending}}),
    CheckedFiles = if Table.RowCount(SortedFiles)=0 then error "No CSV files found. Existing results are stale until a successful refresh." else if Table.RowCount(SortedFiles)>10000 then error "Workbook limit: 10,000 files per refresh" else SortedFiles,
    Loaded = List.Transform(Table.ToRecords(CheckedFiles),(f) =>
        let Attempt=try LoadFile(f),
            Bad=Attempt[HasError],
            ErrorText=if Bad then (try Attempt[Error][Message] otherwise "File could not be parsed") else "",
            RowTable=if Bad then #table(Table.ColumnNames(EmptyRows),{List.Repeat({null},8)&{f[Name],0,"File issue",ErrorText,"","",""}}) else Attempt[Value][Rows]
        in [Name=f[Name],Rows=RowTable,InputRows=if Bad then 0 else Attempt[Value][Count],FileIssues=if Bad then 1 else 0]),
    GoodTables = List.Transform(List.Select(Loaded,each [FileIssues]=0), each [Rows]),
    Good = if List.Count(GoodTables)=0 then #table(Fields&{"SourceFile","SourceRow","Issues","Fingerprint","GroupKey","RawOrderDate","RawSales","RawRecord"},{}) else Table.Combine(GoodTables),
    Groups = Table.Group(Good,{"GroupKey"},{{"Data",(t) =>
        let Sorted=Table.Sort(t,{{"SourceFile",Order.Ascending},{"SourceRow",Order.Ascending}}),
            Conflict=Table.RowCount(t)>1 and (List.Count(List.Distinct(t[Fingerprint]))>1 or List.AnyTrue(List.Transform(t[Issues],each List.Count(_)>0))),
            Ranked=Table.AddIndexColumn(Sorted,"CopyIndex",0,1,Int64.Type),
            Status=Table.AddColumn(Ranked,"Status",each if Conflict or List.Count([Issues])>0 then "Needs review" else if [CopyIndex]=0 then "Clean" else "Repeat skipped",type text),
            Reason=Table.AddColumn(Status,"Reason",each Text.Combine([Issues] & (if Conflict then {"Conflicting RowID; review every copy"} else if [Status]="Repeat skipped" then {"Identical normalized RowID; retained first source file/row"} else {}),"; "),type text)
        in Table.SelectColumns(Reason,Table.ColumnNames(EmptyRows)),type table}}),
    Classified = if Table.RowCount(Groups)=0 then EmptyRows else Table.Combine(Groups[Data]),
    FileErrors = List.Transform(List.Select(Loaded,each [FileIssues]>0),each [Rows]),
    CombinedUnchecked = Table.Combine({Classified} & FileErrors),
    Combined = if List.Sum(List.Transform(Loaded,each [InputRows]))>100000 then error "Workbook limit: 100,000 parsed rows per refresh" else CombinedUnchecked,
    Rows = Table.TransformColumnTypes(Table.Sort(Combined,{{"SourceFile",Order.Ascending},{"SourceRow",Order.Ascending}}),
        {{"RowID",type text},{"OrderID",type text},{"ProductID",type text},{"OrderDate",type date},{"ShipDate",type date},{"Sales",Currency.Type},{"SourceRow",Int64.Type}}),
    RefreshTime = DateTime.FixedLocalNow(),
    Logs = List.Transform(Loaded,(f) =>
        let t=Table.SelectRows(Rows,each [SourceFile]=f[Name])
        in [SourceFile=f[Name],InputRows=f[InputRows],CleanRows=Table.RowCount(Table.SelectRows(t,each [Status]="Clean")),
            ReviewRows=Table.RowCount(Table.SelectRows(t,each [Status]="Needs review")),RepeatedRows=Table.RowCount(Table.SelectRows(t,each [Status]="Repeat skipped")),
            FileIssues=f[FileIssues],LastRefresh=RefreshTime,SourceFolder=Folder]),
    Files = Table.FromRecords(Logs)
in
    [Rows=Rows,Files=Files]
