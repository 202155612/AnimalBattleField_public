DO $$
DECLARE
    src_schema text := current_user;
    r record;
BEGIN
    FOR r IN 
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = src_schema
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.%I SET SCHEMA public;',
            src_schema,
            r.tablename
        );
    END LOOP;

    FOR r IN
        SELECT viewname
        FROM pg_views
        WHERE schemaname = src_schema
    LOOP
        EXECUTE format(
            'ALTER VIEW %I.%I SET SCHEMA public;',
            src_schema,
            r.viewname
        );
    END LOOP;

    FOR r IN
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = src_schema
    LOOP
        EXECUTE format(
            'ALTER SEQUENCE %I.%I SET SCHEMA public;',
            src_schema,
            r.sequence_name
        );
    END LOOP;
END
$$;


GRANT SELECT ON card_info TO guest;
GRANT SELECT ON deck_info TO player;
GRANT SELECT ON card_stats TO guest;
GRANT SELECT ON login_data TO guest;
GRANT SELECT ON account_data TO player;
GRANT SELECT ON deck_card_info TO player;
GRANT SELECT ON deck_complete TO player;
GRANT SELECT ON deck_match TO player;
GRANT SELECT ON card_abilities TO developer;
GRANT SELECT ON match_list TO guest;
GRANT SELECT ON match_card_patch TO guest;
GRANT SELECT ON match_turn TO guest;
GRANT SELECT ON account_data TO guest;



GRANT USAGE ON SCHEMA public TO guest, player, developer, administrator;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO player, developer, administrator;