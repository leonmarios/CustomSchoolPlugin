<?php
function class_management_create_tables() {
    global $wpdb;
    $charset_collate = $wpdb->get_charset_collate();

    $classes_table = $wpdb->prefix . 'classes';
    $students_table = $wpdb->prefix . 'students';
    $schedules_table = $wpdb->prefix . 'schedules';

    $sql = "
        CREATE TABLE $classes_table (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            weekly_schedule TEXT,
            PRIMARY KEY (id)
        ) $charset_collate;

        CREATE TABLE $students_table (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            class_id INT,
            PRIMARY KEY (id),
            KEY class_id (class_id)
        ) $charset_collate;

        CREATE TABLE $schedules_table (
            id INT NOT NULL AUTO_INCREMENT,
            class_id INT,
            date DATE,
            time TIME,
            location VARCHAR(255),
            PRIMARY KEY (id),
            KEY class_id (class_id)
        ) $charset_collate;
    ";

    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}
?>
