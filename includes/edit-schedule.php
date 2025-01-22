
<?php
function edit_schedule_form($atts) {
    global $wpdb;
    $class_id = intval($atts['class_id']);
    $table = $wpdb->prefix . 'classes';

    if (isset($_POST['update_schedule'])) {
        $wpdb->update($table, [
            'weekly_schedule' => sanitize_textarea_field($_POST['weekly_schedule']),
        ], ['id' => $class_id]);

        echo "<p>Schedule updated successfully!</p>";
    }

    $class = $wpdb->get_row($wpdb->prepare("SELECT * FROM $table WHERE id = %d", $class_id));
    ?>
    <form method="post">
        <label>Weekly Schedule:</label>
        <textarea name="weekly_schedule" rows="5" required><?php echo esc_textarea($class->weekly_schedule); ?></textarea>
        <br>
        <button type="submit" name="update_schedule">Update Schedule</button>
    </form>
    <?php
}
add_shortcode('edit_schedule_form', 'edit_schedule_form');
?>
