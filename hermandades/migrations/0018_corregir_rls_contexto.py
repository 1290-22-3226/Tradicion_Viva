from django.db import migrations


FIX_SQL = """
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

ALTER POLICY tradicion_viva_devoto_organization_policy ON hermandades_devoto
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

ALTER POLICY tradicion_viva_evento_organization_policy ON hermandades_eventoagenda
USING (
    current_setting('app.current_organization_id', true) = '*'
    OR hermandad_id = tradicion_viva_current_organization_id()
)
WITH CHECK (
    current_setting('app.current_organization_id', true) = '*'
    OR hermandad_id = tradicion_viva_current_organization_id()
);

ALTER POLICY tradicion_viva_turno_organization_policy ON hermandades_turnorecorrido
USING (
    current_setting('app.current_organization_id', true) = '*'
    OR hermandad_id = tradicion_viva_current_organization_id()
)
WITH CHECK (
    current_setting('app.current_organization_id', true) = '*'
    OR hermandad_id = tradicion_viva_current_organization_id()
);

ALTER POLICY tradicion_viva_comunicado_organization_policy ON hermandades_comunicado
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

ALTER POLICY tradicion_viva_envio_organization_policy ON hermandades_enviocomunicado
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


def fix_rls_context(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.connection.cursor().execute(FIX_SQL)


class Migration(migrations.Migration):
    dependencies = [
        ("hermandades", "0017_rls_organizacion"),
    ]

    operations = [
        migrations.RunPython(
            code=fix_rls_context,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
