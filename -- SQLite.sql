-- SQLite
SELECT p.url FROM categories AS p
                    LEFT JOIN categories AS s
                    ON p.id = s.parent_id
                    WHERE s.name is Null
                    ;