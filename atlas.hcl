data "external_schema" "sqlalchemy" {
    program = [
        "uv", "run",
        "atlas-provider-sqlalchemy",
        "--path", "./src/Tickets/db",
        "--dialect", "mysql"
    ]
}

env "sqlalchemy" {
    src = data.external_schema.sqlalchemy.url
    dev = "docker://mysql/8/dev"
    migration {
        dir = "file://src/Tickets/db/migrations"
    }
    format {
        migrate {
            diff = "{{ sql . \"  \" }}"
        }
    }
}