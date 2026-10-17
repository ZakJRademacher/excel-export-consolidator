let
    Source = Consolidation[Rows],
    Issues = Table.SelectRows(Source,each [Status]<>"Clean"),
    Action = Table.AddColumn(Issues,"Action",each if [Status]="Repeat skipped" then "No action unless repeat was intentional" else if [Status]="File issue" then "Check filename profile, headers and CSV structure" else "Correct source record, save CSV, then Refresh All",type text),
    Result = Table.SelectColumns(Action,{"Status","RowID","Reason","SourceFile","SourceRow","RawOrderDate","RawSales","Action","RawRecord"})
in
    Result
