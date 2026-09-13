{% macro swap_mart_schema() %} 
    {#- 
        Atomically promotes the freshly-built "mart_next" schema to 
        "mart" -- the schema the Streamlit dashboard reads from. 
 
        Sequence: rename current "mart" to "mart_old", rename 
        "mart_next" to "mart", then rename "mart_old" into the 
        "mart_next" slot so the next run has a shadow schema ready to 
        build into. All three renames run inside one transaction. 
        Postgres DDL is transactional, so a crash mid-swap rolls back 
        entirely -- there is no intermediate state where "mart" is 
        missing or half-renamed for a reader to observe. 
 
        Call this only after `dbt run --select marts` and 
        `dbt test --select marts` have both succeeded. If tests fail, 
        don't call this: "mart" keeps serving the last good build, and 
        "mart_next" holds the untested build for inspection. 
    -#} 
 
    {% set existing_schemas_sql %} 
        select nspname from pg_namespace 
        where nspname in ('mart', 'mart_next', 'mart_old') 
    {% endset %} 
 
    {% set results = run_query(existing_schemas_sql) %} 
    {% set existing = results.columns[0].values() if execute else [] %} 
 
    {% if 'mart_next' not in existing %} 
        {{ exceptions.raise_compiler_error( 
            "mart_next schema does not exist -- run `dbt run --select marts` " 
            "before promoting." 
        ) }} 
    {% endif %} 
 
    {% set swap_sql %} 
        begin; 
        {% if 'mart' in existing %} 
        alter schema mart rename to mart_old; 
        {% endif %} 
        alter schema mart_next rename to mart; 
        {% if 'mart' in existing %} 
        alter schema mart_old rename to mart_next; 
        {% endif %} 
        commit; 
    {% endset %} 
 
    {% do run_query(swap_sql) %} 
 
    {{ log( 
        "Promoted mart_next -> mart" ~ 
        (" (previous mart -> mart_next, ready for next build)" if 'mart' in existing else ""), 
        info=True 
    ) }} 
 
{% endmacro %} 
    