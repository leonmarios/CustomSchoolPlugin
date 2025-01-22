
<?php
class CreateClass {
    public static function create_class_form() {
        global $wpdb;

        // Days and Time Slots
        $days = ['Δευτέρα', 'Τρίτη', 'Τετάρτη', 'Πέμπτη', 'Παρασκευή'];
        $time_slots = [
            '9:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
            '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'
        ];

        // Handle form submission
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['create_class'])) {
            // Sanitize input
            $class_name = sanitize_text_field($_POST['class_name']);
            $class_description = sanitize_textarea_field($_POST['class_description']);

            // Insert class into database
            $wpdb->insert(
                "{$wpdb->prefix}classes",
                [
                    'name' => $class_name,
                    'description' => $class_description,
                    'created_at' => current_time('mysql'),
                ]
            );

            $class_id = $wpdb->insert_id;

            // Insert schedule into database
            if ($class_id && isset($_POST['schedule'])) {
                foreach ($_POST['schedule'] as $day => $slots) {
                    foreach ($slots as $time_slot => $subject) {
                        if (!empty($subject)) {
                            $wpdb->insert(
                                "{$wpdb->prefix}class_schedule",
                                [
                                    'class_id' => $class_id,
                                    'day' => sanitize_text_field($day),
                                    'time_slot' => sanitize_text_field($time_slot),
                                    'subject' => sanitize_text_field($subject),
                                    'created_at' => current_time('mysql'),
                                    'updated_at' => current_time('mysql'),
                                ]
                            );
                        }
                    }
                }
            }

            if ($class_id) {
                echo '<p>Το τμήμα δημιουργήθηκε με επιτυχία με ID: ' . esc_html($class_id) . '</p>';
                wp_redirect($_SERVER['REQUEST_URI']);
                exit;
            } else {
                echo '<p>Σφάλμα. Το τμήμα δεν μπορούσε να δημιουργηθεί.</p>';
            }
        }

        // Render the form
        ?>
        <div class="plugin-form-container">
            <h2>Δημιουργία τμήματος</h2>
            <form method="POST">
                <div class="plugin-form-group">
                    <label for="class_name">Τμήμα:</label>
                    <input type="text" id="class_name" name="class_name" required>
                </div>

                <div class="plugin-form-group">
                    <label for="class_description">Περιγραφή:</label>
                    <textarea id="class_description" name="class_description" rows="5"></textarea>
                </div>

                <h3>Ωριαίο πρόγραμμα</h3>
                <table class="class-schedule-table">
                    <thead>
                        <tr>
                            <th>Διδακτική ώρα</th>
                            <?php foreach ($days as $day): ?>
                                <th><?php echo esc_html($day); ?></th>
                            <?php endforeach; ?>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($time_slots as $time_slot): ?>
                            <tr>
                                <td><?php echo esc_html($time_slot); ?></td>
                                <?php foreach ($days as $day): ?>
                                    <td>
                                        <input
                                            type="text"
                                            name="schedule[<?php echo esc_attr($day); ?>][<?php echo esc_attr($time_slot); ?>]"
                                            placeholder="Μάθημα"
                                        >
                                    </td>
                                <?php endforeach; ?>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>

                <button type="submit" name="create_class">Δημιουργία τμήματος</button>
            </form>
        </div>
        <?php
    }
}

// Register the shortcode to display the class creation form
add_shortcode('create_class_form', ['CreateClass', 'create_class_form']);
?>
