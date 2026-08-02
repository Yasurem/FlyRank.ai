CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN DEFAULT false
);

INSERT INTO tasks (title, done)
SELECT title, done
FROM (
    SELECT 'Brush teeth' AS title, '1'::boolean AS done UNION ALL
    SELECT 'Review Statistics' AS title, '1'::boolean AS done UNION ALL
    SELECT 'Finish FlyRank Assignment' AS title, '0'::boolean AS done
) WHERE (SELECT COUNT(*) FROM tasks) = 0;


