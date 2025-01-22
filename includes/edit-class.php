<?php
class EditClass {
    public static function edit_class_form() {
        global $wpdb;

        // Fetch all classes for the dropdown
        $classes = $wpdb->get_results("SELECT id, name FROM {$wpdb->prefix}classes");

        // Days and Time Slots
        $days = ['Δευτέρα', 'Τρίτη', 'Τετάρτη', 'Πέμπτη', 'Παρασκευή'];
        $time_slots = [
            '9:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
            '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'
        ];

        ?>
        <div class="plugin-form-container">
            <h2>Επεξεργασία τμήματος</h2>
            <form id="edit-class-form" method="POST">
                <div class="plugin-form-group">
                    <label for="class_id">Επιλογή τμήματος:</label>
                    <select id="class_id" name="class_id" required>
                        <option value="">-- Επιλέξτε τμήμα --</option>
                        <?php foreach ($classes as $class): ?>
                            <option value="<?php echo esc_attr($class->id); ?>">
                                <?php echo esc_html($class->name); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <div id="class-details" style="display: none;">
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

                    <button type="submit" name="edit_class">Αποθήκευση αλλαγών</button>
                </div>
            </form>
        </div>

        <script>
            document.getElementById('class_id').addEventListener('change', function () {
                const classId = this.value;

                if (classId) {
                    fetch(ajaxurl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `action=fetch_class_details&class_id=${classId}`
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('class_name').value = data.class.name || '';
                            document.getElementById('class_description').value = data.class.description || '';

                            // Clear previous schedule inputs
                            document.querySelectorAll('.class-schedule-table input').forEach(input => {
                                input.value = '';
                            });

                            // Populate schedule
                            const schedule = data.schedule || {};
                            for (const [day, slots] of Object.entries(schedule)) {
                                for (const [time_slot, subject] of Object.entries(slots)) {
                                    const input = document.querySelector(
                                        `input[name="schedule[${day}][${time_slot}]"]`
                                    );
                                    if (input) input.value = subject;
                                }
                            }

                            document.getElementById('class-details').style.display = 'block';
                        } else {
                            alert('Σφάλμα κατά τη φόρτωση των στοιχείων του τμήματος.');
                        }
                    });
                } else {
                    // Hide the details section if no class is selected
                    document.getElementById('class-details').style.display = 'none';

                    // Clear all input fields
                    document.getElementById('class_name').value = '';
                    document.getElementById('class_description').value = '';
                    document.querySelectorAll('.class-schedule-table input').forEach(input => {
                        input.value = '';
                    });
                }
            });
        </script>
        <?php
    }

    public static function fetch_class_details() {
        global $wpdb;

        $class_id = intval($_POST['class_id']);
        $class = $wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->prefix}classes WHERE id = %d", $class_id), ARRAY_A);
        $schedule_results = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM {$wpdb->prefix}class_schedule WHERE class_id = %d",
            $class_id
        ));

        $schedule = [];
        foreach ($schedule_results as $entry) {
            $schedule[$entry->day][$entry->time_slot] = $entry->subject;
        }

        wp_send_json([
            'success' => true,
            'class' => $class,
            'schedule' => $schedule
        ]);
    }
}

// Register the shortcode to display the class editing form
add_shortcode('edit_class_form', ['EditClass', 'edit_class_form']);

// Register AJAX action for fetching class details
add_action('wp_ajax_fetch_class_details', ['EditClass', 'fetch_class_details']);
add_action('wp_ajax_nopriv_fetch_class_details', ['EditClass', 'fetch_class_details']);
?>
