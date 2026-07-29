data "external_schema" "sqlalchemy" {
    program = [
        "uv", "run",
        "atlas-provider-sqlalchemy",
        "--path", "./db",
        "--dialect", "mysql"
    ]
}

env "sqlalchemy" {
    src = data.external_schema.sqlalchemy.url
    dev = "docker://mysql/8/dev"
    migration {
        dir = "file://migrations"
    }
    format {
        migrate {
            diff = "{{ sql . \"  \" }}"
        }
    }
}