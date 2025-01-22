
<?php
function create_class_form() {
    if (isset($_POST['create_class'])) {
        global $wpdb;
        $table = $wpdb->prefix . 'classes';

        $wpdb->insert($table, [
            'name' => sanitize_text_field($_POST['class_name']),
            'description' => sanitize_textarea_field($_POST['class_description']),
        ]);

        echo "<p>Class created successfully!</p>";
    }
    ?>
    <form method="post">
        <label>Class Name:</label>
        <input type="text" name="class_name" required>
        <br>
        <label>Class Description:</label>
        <textarea name="class_description" rows="4" required></textarea>
        <br>
        <button type="submit" name="create_class">Create Class</button>
    </form>
    <?php
}
add_shortcode('create_class_form', 'create_class_form');
?>
