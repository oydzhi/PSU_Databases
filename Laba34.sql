DROP TABLE IF EXISTS spec_table;
CREATE TABLE spec_table (
	id_row INT PRIMARY KEY,
	name_table VARCHAR(100),
	name_column VARCHAR(100),
	maximum INT
);

INSERT INTO spec_table (id_row, name_table, name_column, maximum) VALUES (1, 'spec', 'id', 1);

CREATE OR REPLACE FUNCTION func1(p_name_table VARCHAR, p_name_column VARCHAR) RETURNS INTEGER AS $$
DECLARE
    v_next_id INT;
    v_max_value INT;
BEGIN
    SELECT maximum INTO v_max_value FROM spec_table 
    WHERE name_table = p_name_table AND name_column = p_name_column;

    IF v_max_value IS NOT NULL THEN
        v_next_id := v_max_value + 1;
        UPDATE spec_table SET maximum = v_next_id 
        WHERE name_table = p_name_table AND name_column = p_name_column;
    ELSE
        EXECUTE format('SELECT COALESCE(MAX(%I), 0) FROM %I', p_name_column, p_name_table) INTO v_max_value;
        v_next_id := v_max_value + 1;
        INSERT INTO spec_table (id_row, name_table, name_column, maximum) VALUES (v_max_value, p_name_table, p_name_column, v_next_id);
    END IF;
	
	RETURN v_next_id;
END; $$ LANGUAGE plpgsql;

SELECT func1('spec', 'id');
SELECT * FROM spec_table;

SELECT func1('spec', 'id');
SELECT * FROM spec_table;


DROP TABLE IF EXISTS test;
CREATE TABLE test (
    id INT
);
INSERT INTO test (id) VALUES (10);


SELECT func1('test', 'id');
SELECT * FROM spec_table; 

SELECT func1('test', 'id');
SELECT * FROM spec_table;

DROP TABLE IF EXISTS test2;
CREATE TABLE test2 (
    num_value1 INT,
    num_value2 INT
);

SELECT func1('test2', 'num_value1'); 
SELECT * FROM spec_table; -- Ожидаем (1, spec, id, 5), (4, test, id, 12), (5, test2, num_value1, 1)


INSERT INTO test2 (num_value1, num_value2) VALUES (2, 13);
SELECT func1('test2', 'num_value2'); -- Ожидаем 14


SELECT * FROM spec_table;

--func1('test2', 'num_value1');


SELECT * FROM spec_table; -- Ожидаем (1, spec, id, 6), (4, test, id, 12), (5, test2, num_value1, 2), (6, test2, num_value2, 14)

CREATE OR REPLACE FUNCTION update_maximum() RETURNS TRIGGER AS $$
DECLARE
    v_max_value INT;
    v_new_value INT;
BEGIN
    SELECT maximum INTO v_max_value FROM spec_table 
    WHERE name_table = TG_TABLE_NAME AND name_column = TG_ARGV[0];

    EXECUTE format('SELECT $1.%I', TG_ARGV[0]) INTO v_new_value USING NEW;

    IF v_new_value > v_max_value THEN
        UPDATE spec_table SET maximum = v_new_value 
        WHERE name_table = TG_TABLE_NAME AND name_column = TG_ARGV[0];
    END IF;

    RETURN NEW;
END; $$ LANGUAGE plpgsql;


CREATE TRIGGER test2_num_value1_trigger AFTER INSERT OR UPDATE ON test2
FOR EACH ROW EXECUTE FUNCTION update_maximum('num_value1');

CREATE TRIGGER test2_num_value2_trigger AFTER INSERT OR UPDATE ON test2
FOR EACH ROW EXECUTE FUNCTION update_maximum('num_value2');


INSERT INTO test2 (num_value1, num_value2) VALUES (3, 15);

SELECT * FROM spec_table; 

UPDATE test2 SET num_value1 = 5 WHERE num_value1 = 3;
SELECT * FROM spec_table; 

INSERT INTO test2 (num_value1, num_value2) VALUES (4, 16);

SELECT * FROM spec_table;


