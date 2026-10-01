from django.db import migrations


FORWARD_SQL = """
CREATE OR REPLACE FUNCTION tradicion_viva_current_organization_id()
RETURNS bigint
LANGUAGE SQL
STABLE
SECURITY INVOKER
SET search_path = pg_catalog
AS $$
    SELECT CASE
        WHEN current_setting('app.current_organization_id', true) ~ '^[0-9]+$'
        THEN current_setting('app.current_organization_id', true)::bigint
        ELSE NULL
    END;
$$;

CREATE OR REPLACE FUNCTION tradicion_viva_current_account_id()
RETURNS bigint
LANGUAGE SQL
STABLE
SECURITY INVOKER
SET search_path = pg_catalog
AS $$
    SELECT CASE
        WHEN current_setting('app.current_account_id', true) ~ '^[0-9]+$'
        THEN current_setting('app.current_account_id', true)::bigint
        ELSE NULL
    END;
$$;

ALTER TABLE hermandades_devoto ENABLE ROW LEVEL SECURITY;
ALTER TABLE hermandades_devoto FORCE ROW LEVEL SECURITY;
CREATE POLICY tradicion_viva_devoto_organization_policy
    ON hermandades_devoto
    USING (
        current_setting('app.current_organization_id', true) = '*'
        OR hermandad_id = tradicion_viva_current_organization_id()
        OR (
            cuenta_id IS NOT NULL
            AND cuenta_id = tradicion_viva_current_account_id()
        )
    )
    WITH CHECK (
        current_setting('app.current_organization_id', true) = '*'
        OR hermandad_id = tradicion_viva_current_organization_id()
        OR (
            cuenta_id IS NOT NULL
            AND cuenta_id = tradicion_viva_current_account_id()
        )
    );

ALTER TABLE hermandades_eventoagenda ENABLE ROW LEVEL SECURITY;
ALTER TABLE hermandades_eventoagenda FORCE ROW LEVEL SECURITY;
CREATE POLICY tradicion_viva_evento_organization_policy
    ON hermandades_eventoagenda
    USING (
        current_setting('app.current_organization_id', true) = '*'
        OR hermandad_id = tradicion_viva_current_organization_id()
    )
    WITH CHECK (
        current_setting('app.current_organization_id', true) = '*'
        OR hermandad_id = tradicion_viva_current_organization_id()
    );

ALTER TABLE hermandades_turnorecorrido ENABLE ROW LEVEL SECURITY;
ALTER TABLE hermandades_turnorecorrido FORCE ROW LEVEL SECURITY;
CREATE POLICY tradicion_viva_turno_organization_policy
    ON hermandades_turnorecorrido
    USING (
        current_setting('app.current_organization_id', true) = '*'
        OR hermandad_id = tradicion_viva_current_organization_id()
    )
    WITH CHECK (
        current_setting('app.current_organization_id', true) = '*'
        OR hermandad_id = tradicion_viva_current_organization_id()
    );

ALTER TABLE hermandades_comunicado ENABLE ROW LEVEL SECURITY;
ALTER TABLE hermandades_comunicado FORCE ROW LEVEL SECURITY;
CREATE POLICY tradicion_viva_comunicado_organization_policy
    ON hermandades_comunicado
    USING (
        current_setting('app.current_organization_id', true) = '*'
        OR (
            hermandad_id IS NOT NULL
            AND hermandad_id = tradicion_viva_current_organization_id()
        )
    )
    WITH CHECK (
        current_setting('app.current_organization_id', true) = '*'
        OR (
            hermandad_id IS NOT NULL
            AND hermandad_id = tradicion_viva_current_organization_id()
        )
    );

ALTER TABLE hermandades_enviocomunicado ENABLE ROW LEVEL SECURITY;
ALTER TABLE hermandades_enviocomunicado FORCE ROW LEVEL SECURITY;
CREATE POLICY tradicion_viva_envio_organization_policy
    ON hermandades_enviocomunicado
    USING (
        current_setting('app.current_organization_id', true) = '*'
        OR EXISTS (
            SELECT 1
            FROM hermandades_comunicado comunicado
            WHERE comunicado.id = comunicado_id
              AND comunicado.hermandad_id = tradicion_viva_current_organization_id()
        )
    )
    WITH CHECK (
        current_setting('app.current_organization_id', true) = '*'
        OR EXISTS (
            SELECT 1
            FROM hermandades_comunicado comunicado
            WHERE comunicado.id = comunicado_id
              AND comunicado.hermandad_id = tradicion_viva_current_organization_id()
        )
    );
"""


REVERSE_SQL = """
DROP POLICY IF EXISTS tradicion_viva_envio_organization_policy ON hermandades_enviocomunicado;
ALTER TABLE hermandades_enviocomunicado NO FORCE ROW LEVEL SECURITY;
ALTER TABLE hermandades_enviocomunicado DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tradicion_viva_comunicado_organization_policy ON hermandades_comunicado;
ALTER TABLE hermandades_comunicado NO FORCE ROW LEVEL SECURITY;
ALTER TABLE hermandades_comunicado DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tradicion_viva_turno_organization_policy ON hermandades_turnorecorrido;
ALTER TABLE hermandades_turnorecorrido NO FORCE ROW LEVEL SECURITY;
ALTER TABLE hermandades_turnorecorrido DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tradicion_viva_evento_organization_policy ON hermandades_eventoagenda;
ALTER TABLE hermandades_eventoagenda NO FORCE ROW LEVEL SECURITY;
ALTER TABLE hermandades_eventoagenda DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tradicion_viva_devoto_organization_policy ON hermandades_devoto;
ALTER TABLE hermandades_devoto NO FORCE ROW LEVEL SECURITY;
ALTER TABLE hermandades_devoto DISABLE ROW LEVEL SECURITY;
DROP FUNCTION IF EXISTS tradicion_viva_current_account_id();
DROP FUNCTION IF EXISTS tradicion_viva_current_organization_id();
"""


def apply_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.connection.cursor().execute(FORWARD_SQL)


def remove_rls(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.connection.cursor().execute(REVERSE_SQL)


class Migration(migrations.Migration):
    dependencies = [
        ("hermandades", "0016_remove_cuentadevoto_google_subject"),
    ]

    operations = [
        migrations.RunPython(
            code=apply_rls,
            reverse_code=remove_rls,
        ),
    ]
