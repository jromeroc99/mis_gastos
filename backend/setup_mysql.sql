-- Script para configurar MySQL para mis_gastos
-- Ejecutar como root: sudo mysql < setup_mysql.sql

-- Crear bases de datos
CREATE DATABASE IF NOT EXISTS mis_gastos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS mis_gastos_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario
CREATE USER IF NOT EXISTS 'mis_gastos_user'@'localhost' IDENTIFIED BY 'dev_password_123';

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON mis_gastos.* TO 'mis_gastos_user'@'localhost';
GRANT ALL PRIVILEGES ON mis_gastos_test.* TO 'mis_gastos_user'@'localhost';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar
SELECT user, host FROM mysql.user WHERE user = 'mis_gastos_user';
SHOW DATABASES LIKE 'mis_gastos%';
