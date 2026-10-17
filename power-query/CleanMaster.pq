let
    Source = Consolidation[Rows],
    Clean = Table.SelectRows(Source,each [Status]="Clean"),
    Result = Table.SelectColumns(Clean,{"RowID","OrderID","OrderDate","ShipDate","Category","Region","ProductID","Sales","SourceFile","SourceRow"})
in
    Result
