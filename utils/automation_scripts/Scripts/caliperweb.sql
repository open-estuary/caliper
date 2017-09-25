CREATE USER caliperuser WITH PASSWORD 'caliperts';
CREATE DATABASE calipernewdb OWNER caliperuser;
GRANT ALL PRIVILEGES ON DATABASE calipernewdb to caliperuser;
