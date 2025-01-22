
<?php
function delete_class_form() {
    if (isset($_POST['delete_class'])) {
        global $wpdb;
        $table = $wpdb->prefix . 'classes';
        $class_id = intval($_POST['class_id']);

        $wpdb->delete($table, ['id' => $class_id]);

        echo "<p>Class deleted successfully!</p>";
    }

    $classes = $wpdb->get_results("SELECT * FROM {$wpdb->prefix}classes");
    ?>
    <form method="post">
        <label>Select Class to Delete:</label>
        <select name="class_id" required>
            <?php foreach ($classes as $class): ?>
                <option value="<?php echo esc_attr($class->id); ?>"><?php echo esc_html($class->name); ?></option>
            <?php endforeach; ?>
        </select>
        <br>
        <button type="submit" name="delete_class">Delete Class</button>
    </form>
    <?php
}
add_shortcode('delete_class_form', 'delete_class_form');
?>
