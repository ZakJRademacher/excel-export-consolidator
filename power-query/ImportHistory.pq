let
    Source = Consolidation[Files],
    Result = Table.TransformColumnTypes(Source,{{"InputRows",Int64.Type},{"CleanRows",Int64.Type},{"ReviewRows",Int64.Type},{"RepeatedRows",Int64.Type},{"FileIssues",Int64.Type},{"LastRefresh",type datetime}})
in
    Result
