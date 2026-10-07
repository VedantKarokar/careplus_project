data "external_schema" "sqlalchemy" {
    program = [
        "uv", "run",
        "atlas-provider-sqlalchemy",
        "--path", "./src/tickets_pipeline/db",
        "--dialect", "mysql"
    ]
}

env "sqlalchemy" {
    src = data.external_schema.sqlalchemy.url
    dev = "docker://mysql/8/dev"
    migration {
        dir = "file://src/tickets_pipeline/db/migrations"
    }
    format {
        migrate {
            diff = "{{ sql . \"  \" }}"
        }
    }
}