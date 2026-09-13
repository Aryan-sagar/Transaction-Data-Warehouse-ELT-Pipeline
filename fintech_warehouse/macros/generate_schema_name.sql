{% macro generate_schema_name(custom_schema_name, node) %}

    {#-
        Marts always build into a shadow schema ("mart_next"), never
        directly into "mart". "mart" is the schema the Streamlit
        dashboard queries, so it should only ever contain a fully
        built and tested set of marts.

        The DAG promotes mart_next -> mart (see swap_mart_schema()) only
        after `dbt run --select marts` AND `dbt test --select marts`
        both succeed. If either fails, mart_next is left as-is for
        inspection and "mart" keeps serving the last known-good build --
        the dashboard never sees a half-rebuilt or failed-test schema.
    -#}

    {% if custom_schema_name is none %}

        {{ target.schema }}

    {% elif custom_schema_name == 'mart' and not var('promote_mart', false) %}

        {{ custom_schema_name | trim }}_next

    {% else %}

        {{ custom_schema_name | trim }}

    {% endif %}

{% endmacro %}