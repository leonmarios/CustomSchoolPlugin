<?php
/*
 Plugin Name: Class Management Plugin
 Description: A plugin to manage classes, students, and schedules in WordPress.
 Version: 4.0
 Author: Marios Leon
*/

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define constants
define('CMP_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('CMP_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include feature files
require_once CMP_PLUGIN_DIR . 'includes/db-tables.php';
require_once CMP_PLUGIN_DIR . 'includes/create-class.php';
require_once CMP_PLUGIN_DIR . 'includes/edit-class.php';
require_once CMP_PLUGIN_DIR . 'includes/delete-class.php';
require_once CMP_PLUGIN_DIR . 'includes/helper-functions.php';
require_once CMP_PLUGIN_DIR . 'includes/create-user.php';
require_once CMP_PLUGIN_DIR . 'includes/manage-schedule.php';

// Enqueue CSS and JS
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('cmp-styles', CMP_PLUGIN_URL . 'assets/css/style.css', [], '1.0');
    wp_enqueue_script('cmp-scripts', CMP_PLUGIN_URL . 'assets/js/script.js', ['jquery'], '1.0', true);
});

// Register shortcode for creating users
add_shortcode('create_user_form', ['CreateUser', 'create_user_form']);

// Activation hook for creating tables
register_activation_hook(__FILE__, ['DBTables', 'create_tables']);
?>
