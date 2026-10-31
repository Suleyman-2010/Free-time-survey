SELECT
	pg_get_constraintdef(pg_constraint.oid)
FROM pg_constraint
JOIN pg_class ON pg_class.oid = pg_constraint.conrelid
JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
WHERE pg_class.relname = 'responses'
AND pg_constraint.contype = 'c'
AND (pg_constraint.conkey::integer[] @> ARRAY(
        SELECT attnum::integer FROM pg_attribute
        WHERE attrelid = pg_class.oid AND attname = %s
));
